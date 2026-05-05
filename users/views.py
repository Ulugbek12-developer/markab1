from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from phones.models import Listing
from orders.models import Order
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib import messages
from .models import User
from django.shortcuts import get_object_or_404

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {user.get_role_display()}!")
            return redirect('phones:home')
        return render(request, 'registration/register.html', {'form': form})

class HeadAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'head_admin'

class HeadAdminDashboardView(HeadAdminRequiredMixin, ListView):
    model = User
    template_name = 'users/head_admin_dashboard.html'
    context_object_name = 'users_list'

    def get_queryset(self):
        return User.objects.exclude(id=self.request.user.id).order_by('role')

class AdminUserManageView(HeadAdminRequiredMixin, View):
    def post(self, request, pk):
        user_to_edit = get_object_or_404(User, pk=pk)
        new_role = request.POST.get('role')
        if new_role in dict(User.USER_ROLE_CHOICES):
            user_to_edit.role = new_role
            # Automatically set is_staff for admin roles
            if new_role in ['staff_seller', 'staff_cashier', 'head_admin']:
                user_to_edit.is_staff = True
            else:
                user_to_edit.is_staff = False
            user_to_edit.save()
            messages.success(request, f"{user_to_edit.username} roli {user_to_edit.get_role_display()}ga o'zgartirildi.")
        return redirect('users:head_dashboard')

class SellPhoneView(View):
    def get(self, request):
        return render(request, 'users/sell.html')

    def post(self, request):
        model = request.POST.get('model')
        memory = request.POST.get('memory')
        battery = request.POST.get('battery')
        condition = request.POST.get('condition')
        price = request.POST.get('price')
        user_phone = request.POST.get('phone')
        image = request.FILES.get('image')

        # Create unapproved listing
        Listing.objects.create(
            title=f"{model} {memory}",
            model_name=model,
            memory=memory,
            battery_health=int(battery) if battery else 100,
            condition=condition,
            price=price,
            seller_phone=user_phone,
            image=image,
            is_approved=False # Admin must approve
        )
        
        # Save to session for profile history
        listings = request.session.get('my_listings', [])
        listings.append(model)
        request.session['my_listings'] = listings
        
        return render(request, 'users/sell_success.html')

class ProfileView(View):
    def get(self, request):
        # Mock data from session or simple query
        my_listings_count = len(request.session.get('my_listings', []))
        return render(request, 'users/profile.html', {
            'listings_count': my_listings_count,
            'orders_count': 0 # Mock
        })
