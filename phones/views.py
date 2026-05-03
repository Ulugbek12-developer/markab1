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
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'categories': Category.objects.all(),
            'branches': Branch.objects.all(),
            'active_category': self.request.GET.get('category', 'all')
        })
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
    def test_func(self): return self.request.user.is_staff
    def get_queryset(self): return Listing.objects.all().order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context

class SellView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'color', 'memory', 'region', 'battery_health', 'condition', 'screen_condition', 'body_condition', 'has_box', 'image', 'seller_phone']
    template_name = 'phones/sell.html'
    success_url = reverse_lazy('phones:home')
    def form_valid(self, form):
        form.instance.seller = self.request.user
        
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
        messages.success(self.request, "E'loningiz qabul qilindi!")
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
        
        context = self.get_context_data()
        context['result'] = {
            'price': my_phone_price,
            'model': data.get('model_name')
        }
        return render(request, self.template_name, context)

class FilterView(ListView):
    model = Listing
    template_name = 'phones/filter.html'
    context_object_name = 'phones'
    def get_queryset(self):
        clean_expired_bookings()
        queryset = Listing.objects.filter(is_approved=True, is_booked=False)
        model = self.request.GET.get('model')
        memory = self.request.GET.get('memory')
        if model: queryset = queryset.filter(model_name__icontains=model)
        if memory: queryset = queryset.filter(memory=memory)
        return queryset

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
    def test_func(self): return self.request.user.is_staff
    def get(self, request, pk):
        get_object_or_404(Branch, pk=pk).delete()
        messages.success(request, "Filial o'chirildi.")
        return redirect('phones:admin_dashboard')