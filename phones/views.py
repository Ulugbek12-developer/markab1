from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
import requests
import os
from dotenv import load_dotenv

from .models import Category, Listing, Favorite, Branch, Review
from .utils import calculate_phone_price, BASE_PRICES

def clean_expired_bookings():
    """Hides expired bookings automatically."""
    Listing.objects.filter(is_booked=True, booked_until__lt=timezone.now()).update(is_booked=False, booked_until=None)

class HomeView(ListView):
    model = Listing
    template_name = 'phones/index.html'
    context_object_name = 'listings'
    paginate_by = 12
    
    def get_queryset(self):
        clean_expired_bookings()
        queryset = Listing.objects.filter(is_approved=True, is_booked=False)
        category_slug = self.request.GET.get('category')
        if category_slug and category_slug != 'all':
            queryset = queryset.filter(category__slug=category_slug)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(model_name__icontains=search)
            )

        model_filter = self.request.GET.get('model')
        if model_filter:
            queryset = queryset.filter(model_name__icontains=model_filter)
        
        custom_filter = self.request.GET.get('filter')
        if custom_filter == 'sale':
            queryset = queryset.filter(is_sale=True)
        elif custom_filter == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'branches': Branch.objects.all(),
            'active_category': self.request.GET.get('category', 'all')
        })
        return context

class CatalogView(TemplateView):
    template_name = 'phones/catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Listing.objects.filter(status='active', is_approved=True)

        # Filters
        brand = self.request.GET.get('brand')
        if brand:
            queryset = queryset.filter(model_name__icontains=brand)

        memory = self.request.GET.get('memory')
        if memory:
            queryset = queryset.filter(memory__icontains=memory)

        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        context['listings'] = queryset
        context['categories'] = Category.objects.all()
        return context

class ListingDetailView(DetailView):
    model = Listing
    template_name = 'phones/detail.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.get_object()
        reviews = listing.reviews.all()
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        price = float(listing.price)
        
        context.update({
            'avg_rating': avg_rating,
            'rating_count': reviews.count(),
            'installment_3': int(price * 1.1 / 3),
            'installment_6': int(price * 1.15 / 6),
            'installment_12': int(price * 1.25 / 12),
            'related_listings': Listing.objects.filter(
                category=listing.category, is_approved=True, is_booked=False
            ).exclude(id=listing.id)[:4]
        })
        return context

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'phones/admin_dashboard.html'
    context_object_name = 'phones'
    def test_func(self): 
        return self.request.user.role in ['head_admin', 'staff_seller', 'staff_cashier'] or self.request.user.is_staff

    def get_queryset(self): 
        # Kassir doesn't see product list to manage, he sees orders/assessments (handled in context)
        if self.request.user.role == 'staff_cashier':
            return Listing.objects.none()
        return Listing.objects.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in ['head_admin', 'staff_cashier']:
            context['orders'] = Order.objects.all().order_by('-created_at')
            context['assessments'] = PriceAssessment.objects.all().order_by('-created_at')
            
            # Statistics for Head Admin
            if self.request.user.role == 'head_admin':
                from .models import SiteAnalytics
                from django.utils import timezone
                today_stats, _ = SiteAnalytics.objects.get_or_create(date=timezone.now().date())
                context['stats'] = today_stats
                context['total_users'] = User.objects.count()
                context['total_listings'] = Listing.objects.count()
                
        context['branches'] = Branch.objects.all()
        return context

class SellView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'color', 'memory', 'region', 'battery_health', 'condition', 'screen_condition', 'body_condition', 'has_box', 'image', 'seller_phone']
    template_name = 'phones/sell.html'
    success_url = reverse_lazy('phones:home')
    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.is_approved = True  # Auto-approve so it shows to others immediately
        
        # Handle string arrays from hidden inputs
        parts_str = self.request.POST.get('replaced_parts_list', '')
        defects_str = self.request.POST.get('defects_list', '')
        form.instance.replaced_parts = parts_str.split(',') if parts_str else []
        form.instance.defects = defects_str.split(',') if defects_str else []
        
        # Handle Box string boolean ("Bor" vs "Yo'q")
        box_str = self.request.POST.get('has_box', '')
        form.instance.has_box = "Bor" in box_str
        
        listing = form.save()
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"🆕 <b>Yangi e'lon!</b>\n\n👤 {self.request.user.username}\n📱 {listing.title}\n💰 {listing.price} so'm"
            try: requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": admin_id, "text": text, "parse_mode": "HTML"})
            except: pass
        messages.success(self.request, "✅ Tabriklaymiz! E'loningiz barchaga ko'rinishni boshladi 🎉")
        return super().form_valid(form)

class ToggleBookingView(View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.is_booked:
            listing.is_booked = False
            listing.booked_until = None
            msg = "Bron bekor qilindi."
        else:
            listing.is_booked = True
            listing.booked_until = timezone.now() + timedelta(hours=48)
            msg = "Telefon 48 soatga bron qilindi!"
        listing.save()
        return JsonResponse({"status": "success", "message": msg})

class InstallmentRequestView(View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"💳 <b>Muddatli to'lov so'rovi!</b>\n\n📱 {listing.title}\n📞 {request.POST.get('phone')}\n📍 {request.POST.get('region')}"
            try: requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": admin_id, "text": text, "parse_mode": "HTML"})
            except: pass
        return JsonResponse({"status": "success"})

class FavoritesView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'phones/favorites.html'
    context_object_name = 'favorites'
    def get_queryset(self): return Favorite.objects.filter(user=self.request.user)

class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
        if not created: favorite.delete()
        return redirect(request.META.get('HTTP_REFERER', 'phones:home'))

class TradeInView(TemplateView):
    template_name = 'phones/trade_in.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['models'] = list(BASE_PRICES.keys())
        target_id = self.request.GET.get('target')
        if target_id: context['target_phone'] = get_object_or_404(Listing, id=target_id)
        return context
    def post(self, request, *args, **kwargs):
        data = request.POST
        my_phone_price = calculate_phone_price({
            'model': data.get('my_model'), 'memory': data.get('my_memory'),
            'battery': data.get('my_battery'), 'condition': data.get('my_condition'),
            'box': data.get('my_box'), 'replaced_parts': request.POST.getlist('my_parts'),
            'defects': request.POST.getlist('my_defects'),
        })
        target_price = float(data.get('target_price', 0)) / 1000000 
        difference = round(target_price - my_phone_price, 1)
        context = self.get_context_data()
        context['result'] = {'my_price': my_phone_price, 'target_price': target_price, 'difference': max(0, difference), 'calculated': True}
        
        # Telegram Notification
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"🔄 <b>Trade-in so'rovi!</b>\n\n"
            text += f"📱 Mijoz telefoni: {data.get('my_model', '?')}\n"
            text += f"💾 Xotira: {data.get('my_memory', '?')}\n"
            text += f"🔋 Batareya: {data.get('my_battery', '?')}%\n"
            text += f"📦 Qutisi: {data.get('my_box', '?')}\n"
            text += f"💰 Baholangan narx: {my_phone_price} mln so'm\n"
            text += f"🎯 Maqsad narx: {target_price} mln so'm\n"
            text += f"💵 Farq: {max(0, difference)} mln so'm"
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": admin_id, "text": text, "parse_mode": "HTML"})
            except: pass
        
        return render(request, self.template_name, context)

class AddReviewView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, id=pk)
        Review.objects.create(listing=listing, user=request.user, rating=int(request.POST.get('rating', 5)), comment=request.POST.get('comment', ''))
        messages.success(request, "Sharhingiz uchun rahmat!")
        return redirect('phones:detail', pk=pk)

class CartView(TemplateView):
    template_name = 'phones/cart.html'

class PriceView(TemplateView):
    template_name = 'phones/price.html'

    def post(self, request, *args, **kwargs):
        data = request.POST
        my_phone_price = calculate_phone_price({
            'model': data.get('model_name'), 
            'storage': data.get('memory'),
            'region': data.get('region'),
            'battery': data.get('battery_health'), 
            'screen_condition': data.get('screen_condition'),
            'body_condition': data.get('body_condition'),
            'box': data.get('has_box'), 
            'replaced_parts': data.get('replaced_parts_list', '').split(','),
            'defects': data.get('defects_list', '').split(','),
        })
        
        # SAVE Assessment to DB
        from .models import PriceAssessment
        PriceAssessment.objects.create(
            user=request.user if request.user.is_authenticated else None,
            model_name=data.get('model_name', 'Unknown'),
            memory=data.get('memory', 'Unknown'),
            battery_health=int(data.get('battery_health', 0)) if data.get('battery_health') else 0,
            calculated_price=my_phone_price,
            details={
                'region': data.get('region'),
                'screen': data.get('screen_condition'),
                'body': data.get('body_condition'),
                'box': data.get('has_box'),
                'parts': data.get('replaced_parts_list'),
                'defects': data.get('defects_list')
            }
        )
        
        context = self.get_context_data()
        context['result'] = {
            'price': my_phone_price,
            'model': data.get('model_name')
        }
        
        # Telegram Notification
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"📊 <b>Narxlash so'rovi!</b>\n\n"
            text += f"📱 Model: {data.get('model_name', '?')}\n"
            text += f"🎨 Rang: {data.get('color', '?')}\n"
            text += f"💾 Xotira: {data.get('memory', '?')}\n"
            text += f"🌍 Region: {data.get('region', '?')}\n"
            text += f"🔋 Batareya: {data.get('battery_health', '?')}%\n"
            text += f"📱 Ekran: {data.get('screen_condition', '?')}\n"
            text += f"📦 Qutisi: {data.get('has_box', '?')}\n"
            text += f"💰 Natija: {my_phone_price} mln so'm"
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={"chat_id": admin_id, "text": text, "parse_mode": "HTML"})
            except: pass
        
        return render(request, self.template_name, context)

class FilterView(ListView):
    model = Listing
    template_name = 'phones/filter.html'
    context_object_name = 'phones'
    def get_queryset(self):
        clean_expired_bookings()
        queryset = Listing.objects.filter(is_approved=True, is_booked=False)
        
        # Get parameters
        model = self.request.GET.get('model')
        color = self.request.GET.get('color')
        memory = self.request.GET.get('memory')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        sort = self.request.GET.get('sort')

        # Apply filters
        if model: queryset = queryset.filter(model_name__icontains=model)
        if color: queryset = queryset.filter(color__iexact=color)
        if memory: queryset = queryset.filter(memory=memory)
        if min_price: queryset = queryset.filter(price__gte=min_price)
        if max_price: queryset = queryset.filter(price__lte=max_price)

        # Apply Sorting
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch unique models and colors from existing listings for the filter UI
        context['available_models'] = Listing.objects.filter(is_approved=True).values_list('model_name', flat=True).distinct().order_by('model_name')
        context['available_colors'] = Listing.objects.filter(is_approved=True).values_list('color', flat=True).distinct().order_by('color')
        return context

class SearchView(ListView):
    model = Listing
    template_name = 'phones/search.html'
    context_object_name = 'phones'
    def get_queryset(self):
        q = self.request.GET.get('q')
        if not q: return Listing.objects.none()
        return Listing.objects.filter(Q(title__icontains=q) | Q(model_name__icontains=q), is_approved=True, is_booked=False)

class AdminDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self): return self.request.user.is_staff
    def get(self, request, pk):
        get_object_or_404(Listing, pk=pk).delete()
        messages.success(request, "O'chirildi.")
        return redirect('phones:admin_dashboard')

class StorePanelView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'color', 'memory', 'region', 'battery_health', 'condition', 'screen_condition', 'body_condition', 'has_box', 'image']
    template_name = 'phones/store_panel.html'
    success_url = reverse_lazy('phones:admin_dashboard')
    def test_func(self): return self.request.user.is_staff
    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.is_approved = True
        
        # Handle Aksiya fields
        form.instance.is_sale = self.request.POST.get('is_sale') == 'on'
        old_price = self.request.POST.get('old_price')
        if old_price:
            form.instance.old_price = old_price
            
        # Additional fields
        form.instance.color = self.request.POST.get('color', '')
        
        return super().form_valid(form)

class AdminBranchCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Branch
    fields = ['name', 'address', 'map_url', 'phone']
    template_name = 'phones/branch_add.html'
    success_url = reverse_lazy('phones:admin_dashboard')
    def test_func(self): return self.request.user.is_staff
    def form_valid(self, form):
        messages.success(self.request, "Filial muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)

class AdminBranchDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self): 
        return self.request.user.role in ['head_admin', 'staff_seller']
    def get(self, request, pk):
        get_object_or_404(Branch, pk=pk).delete()
        messages.success(request, "Filial o'chirildi.")
        return redirect('phones:admin_dashboard')

class NasiyaView(TemplateView):
    template_name = 'phones/nasiya.html'

def nasiya_submit(request):
    import json
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except:
            data = request.POST

        load_dotenv()
        bot_token = os.getenv('BOT_TOKEN', '')
        admin_id = os.getenv('ADMIN_ID', '')

        text = (
            f"📋 <b>Nasiyaga ariza!</b>\n\n"
            f"👤 Ism: {data.get('name', '—')}\n"
            f"📞 Tel: {data.get('phone', '—')}\n"
            f"🎂 Tug'ilgan: {data.get('birthday', '—')} ({data.get('age', '—')} yosh)\n"
            f"💳 Bank karta: {data.get('bank', '—')}\n"
            f"📱 Brend: {data.get('brand', '—')}\n"
            f"💰 Oylik to'lov: {data.get('payment', '—')}\n"
            f"⏰ Qachon: {data.get('when', '—')}"
        )

        if bot_token and admin_id:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={"chat_id": admin_id, "text": text, "parse_mode": "HTML"}
                )
            except:
                pass

        return JsonResponse({"status": "ok"})
    return JsonResponse({"error": "POST only"}, status=405)

class TrackRegionView(View):
    def post(self, request):
        import json
        from .models import SiteAnalytics
        from django.utils import timezone
        try:
            data = json.loads(request.body)
            region = data.get('region')
            if region:
                stats, _ = SiteAnalytics.objects.get_or_create(date=timezone.now().date())
                current_stats = stats.region_stats
                current_stats[region] = current_stats.get(region, 0) + 1
                stats.region_stats = current_stats
                stats.save()
                return JsonResponse({"status": "ok"})
        except: pass
        return JsonResponse({"status": "error"}, status=400)

class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            from .models import SiteAnalytics
            from django.utils import timezone
            stats, _ = SiteAnalytics.objects.get_or_create(date=timezone.now().date())
            stats.total_visits += 1
            stats.save()
        return self.get_response(request)