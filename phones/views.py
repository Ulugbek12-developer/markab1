from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Phone
from django.db.models import Q

class HomeView(ListView):
    model = Phone
    template_name = 'phones/index.html'
    context_object_name = 'phones'
    
    def get_queryset(self):
        return Phone.objects.filter(is_approved=True)

class FilterView(ListView):
    model = Phone
    template_name = 'phones/filter.html'
    context_object_name = 'phones'

    def get_queryset(self):
        queryset = Phone.objects.filter(is_approved=True)
        
        # Get filters
        model = self.request.GET.get('model')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        battery = self.request.GET.get('battery')
        memory = self.request.GET.get('memory')
        condition = self.request.GET.get('condition')
        branch = self.request.GET.get('branch')
        sort = self.request.GET.get('sort')

        if model:
            queryset = queryset.filter(model_name=model)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if memory:
            queryset = queryset.filter(memory=memory)
        if condition:
            queryset = queryset.filter(condition=condition)
        if branch:
            queryset = queryset.filter(branch=branch)
        
        if battery:
            if battery == '70-80':
                queryset = queryset.filter(battery_health__gte=70, battery_health__lt=80)
            elif battery == '80-90':
                queryset = queryset.filter(battery_health__gte=80, battery_health__lt=90)
            elif battery == '90+':
                queryset = queryset.filter(battery_health__gte=90)

        # Sorting
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-created_at')

        return queryset

class SearchView(ListView):
    model = Phone
    template_name = 'phones/search.html'
    context_object_name = 'phones'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Phone.objects.filter(
                Q(model_name__icontains=query) | Q(description__icontains=query),
                is_approved=True
            )
        return Phone.objects.none()

class PhoneDetailView(DetailView):
    model = Phone
    template_name = 'phones/detail.html'
    context_object_name = 'phone'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        phone = self.get_object()
        
        # Installment logic
        price = float(phone.price)
        initial = price * 0.3
        remaining = price - initial
        
        context['installment'] = {
            'initial': int(initial),
            'm3': int(remaining / 3 * 1.1), # +10% interest
            'm6': int(remaining / 6 * 1.15), # +15% interest
            'm12': int(remaining / 12 * 1.25), # +25% interest
        }
        return context

class CalculatorView(View):
    def get(self, request):
        return render(request, 'phones/calculator.html')

    def post(self, request):
        model = request.POST.get('model')
        memory = request.POST.get('memory')
        battery = int(request.POST.get('battery', 100))
        condition = request.POST.get('condition')
        has_box = request.POST.get('has_box') == 'on'
        
        # Simple price logic (base prices)
        base_prices = {
            '11': 300, '12': 450, '13': 600, '14': 750, '15': 950, '16': 1200, '17': 1500,
            '13 Pro': 750, '14 Pro': 900, '15 Pro': 1100, '16 Pro': 1350, '17 Pro': 1600,
            '13 Pro Max': 850, '14 Pro Max': 1050, '15 Pro Max': 1250, '16 Pro Max': 1500, '17 Pro Max': 1800
        }
        
        base = base_prices.get(model, 500)
        
        # Adjustments
        if memory == '256': base += 100
        if memory == '512': base += 250
        if memory == '1024': base += 450
        
        if battery < 85: base *= 0.9
        if battery < 80: base *= 0.85
        
        if condition == 'medium': base *= 0.85
        if condition == 'bad': base *= 0.7
        
        if not has_box: base -= 50
        
        # Convert to mln so'm (approx)
        price_som = int(base * 12700 / 100000) * 100000 # dummy conversion
        
        # Send Telegram Notification
        try:
            from core.telegram_bot import send_admin_notification
            box_txt = 'Bor' if has_box else "Yo'q"
            msg = (
                f"🧮 <b>Kalkulyatorda hisoblandi:</b>\n\n"
                f"📱 Model: {model}\n"
                f"💾 Xotira: {memory} GB\n"
                f"🔋 Batareya: {battery}%\n"
                f"🛠 Holati: {condition}\n"
                f"📦 Karobka: {box_txt}\n\n"
                f"💰 <b>Taxminiy narx: {price_som:,.0f} so'm</b>"
            )
            send_admin_notification(msg)
        except Exception:
            pass
            
        return render(request, 'phones/calculator.html', {
            'result': f"{price_som:,.0f}".replace(',', ' '),
            'posted_data': request.POST
        })

class AdminDashboardView(ListView):
    model = Phone
    template_name = 'phones/admin_dashboard.html'
    context_object_name = 'phones'

    def dispatch(self, request, *args, **kwargs):
        # Oddiy parol tekshiruvi (Session orqali)
        if not request.session.get('is_markab_admin'):
            if request.method == 'POST' and request.POST.get('password') == 'MARKAB777':
                request.session['is_markab_admin'] = True
                return redirect(request.path)
            return render(request, 'phones/admin_login.html')
        return super().dispatch(request, *args, **kwargs)

class AdminAddPhoneView(CreateView):
    model = Phone
    fields = ['model_name', 'branch', 'memory', 'battery_health', 'condition', 'price', 'color', 'region', 'has_box', 'image', 'description']
    template_name = 'phones/admin_add.html'
    success_url = reverse_lazy('phones:admin_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_markab_admin'):
            return redirect('phones:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.is_approved = True
        messages.success(self.request, "Mahsulot muvaffaqiyatli qo'shildi!")
        return super().form_valid(form)

class AdminDeletePhoneView(DeleteView):
    model = Phone
    success_url = reverse_lazy('phones:admin_dashboard')

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_markab_admin'):
            return redirect('phones:admin_dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)
