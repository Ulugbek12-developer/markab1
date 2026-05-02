from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Category, Listing, Favorite
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone

def clean_expired_bookings():
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
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(model_name__icontains=search) |
                Q(category__name__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category', 'all')
        return context

class SearchView(ListView):
    model = Listing
    template_name = 'phones/search.html'
    context_object_name = 'phones'

    def get_queryset(self):
        clean_expired_bookings()
        q = self.request.GET.get('q')
        if not q:
            return Listing.objects.none()
        return Listing.objects.filter(
            Q(title__icontains=q) | 
            Q(description__icontains=q) |
            Q(model_name__icontains=q) |
            Q(category__name__icontains=q),
            is_approved=True,
            is_booked=False
        )

class ListingDetailView(DetailView):
    model = Listing
    template_name = 'phones/detail.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        listing = self.get_object()
        # Installment logic
        price = float(listing.price)
        context['installment_3'] = int(price * 1.1 / 3)
        context['installment_6'] = int(price * 1.15 / 6)
        context['installment_12'] = int(price * 1.25 / 12)
        # Related items
        context['related_listings'] = Listing.objects.filter(
            category=listing.category, is_approved=True
        ).exclude(id=listing.id)[:4]
        return context

class StorePanelView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'memory', 'battery_health', 'condition', 'image']
    template_name = 'phones/store_panel.html'
    success_url = reverse_lazy('phones:admin_dashboard')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.seller = self.request.user
        form.instance.seller_phone = "+998 90 123 45 67" # Rasmiy do'kon raqami
        form.instance.location = "Toshkent"
        form.instance.is_approved = True
        
        apple_category = Category.objects.filter(name__icontains='iPhone').first()
        if not apple_category:
            apple_category = Category.objects.first()
        form.instance.category = apple_category
        
        messages.success(self.request, "Do'kon vitrinasiga muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)

class AdminDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Listing
    template_name = 'phones/admin_dashboard.html'
    context_object_name = 'phones'

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        return Listing.objects.all().order_by('-created_at')

class AdminDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if request.user.is_staff:
            listing.delete()
            messages.success(request, "Mahsulot o'chirildi.")
        return redirect('phones:admin_dashboard')

class SellView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'memory', 'battery_health', 'condition', 'image', 'seller_phone']
    template_name = 'phones/sell.html'
    success_url = reverse_lazy('phones:home')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        listing = form.save()
        
        # Bot notification
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        if bot_token and admin_id:
            text = f"🆕 <b>Yangi e'lon (Veb-saytdan)!</b>\n\n"
            text += f"👤 User: {self.request.user.username}\n"
            text += f"📱 Telefon: {listing.title}\n"
            text += f"💰 Narxi: {listing.price} so'm\n"
            text += f"📞 Aloqa: {listing.seller_phone}"
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
            except: pass

        messages.success(self.request, "E'loningiz qabul qilindi va tekshiruvdan so'ng saytga chiqadi!")
        return super().form_valid(form)

from django.utils import timezone
from datetime import timedelta

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
            msg = "Telefon 2 kunga muvaffaqiyatli bron qilindi!"
            
            # Bot notification
            load_dotenv()
            bot_token = os.environ.get('BOT_TOKEN')
            admin_id = os.environ.get('ADMIN_ID')
            if bot_token and admin_id:
                text = f"🔒 <b>Yangi Bron!</b>\n\n"
                text += f"📱 Telefon: {listing.title}\n"
                text += f"💰 Narxi: {listing.price} so'm\n"
                text += f"⏰ Muddat: 48 soat\n"
                try:
                    requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                        "chat_id": admin_id,
                        "text": text,
                        "parse_mode": "HTML"
                    })
                except: pass
                
        listing.save()
        return JsonResponse({"status": "success", "message": msg})

class PriceView(TemplateView):
    template_name = 'phones/price.html'

import requests
import os
from dotenv import load_dotenv
from django.http import JsonResponse

class InstallmentRequestView(View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        
        region = request.POST.get('region', '')
        city = request.POST.get('city', '')
        months = request.POST.get('months', '')
        monthly = request.POST.get('monthly', '')
        phone = request.POST.get('phone', '')
        
        # Send to Telegram
        load_dotenv()
        bot_token = os.environ.get('BOT_TOKEN')
        admin_id = os.environ.get('ADMIN_ID')
        
        if bot_token and admin_id:
            text = f"🆕 <b>Yangi muddatli to'lov so'rovi!</b>\n\n"
            text += f"📱 Telefon: {listing.title}\n"
            text += f"💰 Umumiy narx: {listing.price} so'm\n\n"
            text += f"📍 Manzil: {region}, {city}\n"
            text += f"🗓 Muddat: {months} oy\n"
            text += f"💵 Oylik to'lov: {monthly} so'm\n\n"
            text += f"📞 Xaridor raqami: {phone}"
            
            try:
                requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data={
                    "chat_id": admin_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
            except Exception as e:
                pass
                
        return JsonResponse({"status": "success"})

class FilterView(ListView):
    model = Listing
    template_name = 'phones/filter.html'
    context_object_name = 'phones'

    def get_queryset(self):
        clean_expired_bookings()
        queryset = Listing.objects.filter(is_approved=True, is_booked=False)
        model = self.request.GET.get('model')
        memory = self.request.GET.get('memory')
        sort = self.request.GET.get('sort')

        if model:
            queryset = queryset.filter(model_name__icontains=model)
        if memory:
            queryset = queryset.filter(memory=memory)
        
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_choices'] = {
            'models': [
                ('15 Pro Max', 'iPhone 15 Pro Max'),
                ('15 Pro', 'iPhone 15 Pro'),
                ('14 Pro Max', 'iPhone 14 Pro Max'),
                ('13 Pro Max', 'iPhone 13 Pro Max'),
                ('12 Pro Max', 'iPhone 12 Pro Max'),
                ('11 Pro Max', 'iPhone 11 Pro Max'),
            ]
        }
        return context

class FavoritesView(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'phones/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
        if not created:
            favorite.delete()
        return redirect(request.META.get('HTTP_REFERER', 'phones:home'))
