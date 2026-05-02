from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Category, Listing, Favorite
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class HomeView(ListView):
    model = Listing
    template_name = 'phones/index.html'
    context_object_name = 'listings'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Listing.objects.filter(is_approved=True)
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['active_category'] = self.request.GET.get('category', 'all')
        return context

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
    success_url = reverse_lazy('phones:home')

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

class SellView(LoginRequiredMixin, CreateView):
    model = Listing
    fields = ['title', 'description', 'price', 'model_name', 'memory', 'battery_health', 'condition', 'image', 'seller_phone']
    template_name = 'phones/sell.html'
    success_url = reverse_lazy('phones:home')

    def form_valid(self, form):
        form.instance.seller = self.request.user
        messages.success(self.request, "E'loningiz qabul qilindi va tekshiruvdan so'ng saytga chiqadi!")
        return super().form_valid(form)

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
