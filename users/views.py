from django.shortcuts import render, redirect
from django.views import View
from phones.models import Listing
from orders.models import Order
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages

class RegisterView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
            return redirect('phones:home')
        return render(request, 'registration/register.html', {'form': form})

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
