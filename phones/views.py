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
        from django.db.models import Q
        from django.utils import timezone
        import datetime
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        return Phone.objects.filter(is_approved=True).filter(
            Q(is_booked=False) | Q(booked_at__lt=two_days_ago)
        )

class FilterView(ListView):
    model = Phone
    template_name = 'phones/filter.html'
    context_object_name = 'phones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_choices'] = {
            'models': Phone._meta.get_field('model_name').choices
        }
        return context

    def get_queryset(self):
        from django.db.models import Q
        from django.utils import timezone
        import datetime
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        queryset = Phone.objects.filter(is_approved=True).filter(
            Q(is_booked=False) | Q(booked_at__lt=two_days_ago)
        )
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
        from django.db.models import Q
        from django.utils import timezone
        import datetime
        two_days_ago = timezone.now() - datetime.timedelta(days=2)
        query = self.request.GET.get('q')
        if query:
            return Phone.objects.filter(
                Q(model_name__icontains=query) | Q(description__icontains=query),
                is_approved=True
            ).filter(
                Q(is_booked=False) | Q(booked_at__lt=two_days_ago)
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
        memory = request.POST.get('memory', '128')
        battery = int(request.POST.get('battery', 100))
        condition = request.POST.get('condition')
        has_box = request.POST.get('has_box') == 'on'
        region = request.POST.get('region', 'll')
        
        # ===== MARKAB NARX JADVALI (USD) =====
        # C-Toifa: 70-80% bat, karobkasiz, KH/J region
        # B-Toifa: 80-90% bat, karobka bor, LL/ZA
        # A-Toifa: 90-100% bat, ideal, LL/ZA
        PRICE_TABLE = {
            #              C      B      A
            '11':        (130,   150,   180),
            '11 Pro':    (150,   180,   220),
            '12':        (190,   220,   260),
            '12 Pro':    (240,   280,   330),
            '12 Pro Max':(320,   370,   430),
            '13':        (280,   320,   370),
            '13 Pro':    (350,   420,   490),
            '13 Pro Max':(500,   580,   650),
            '14':        (350,   400,   460),
            '14 Pro':    (450,   580,   680),
            '14 Pro Max':(550,   650,   770),
            '15':        (500,   570,   650),
            '15 Pro':    (650,   750,   860),
            '15 Pro Max':(850,   950,  1080),
            '16':        (700,   800,   900),
            '16 Pro':    (850,   960,  1080),
            '16 Pro Max':(1050, 1180,  1300),
            '17 Pro Max':(1250, 1400,  1550),
        }
        
        prices = PRICE_TABLE.get(model, (300, 400, 500))
        
        # 1) BATAREYA bo'yicha toifa aniqlash
        if battery >= 90:
            base_price = prices[2]  # A-Toifa
            tier = 'A'
        elif battery >= 80:
            base_price = prices[1]  # B-Toifa
            tier = 'B'
        else:
            base_price = prices[0]  # C-Toifa
            tier = 'C'
        
        # 2) BATAREYA nozik tuzatish
        if battery < 80:
            base_price -= 40   # 80% dan past — qo'shimcha -40$
        if battery >= 95:
            base_price += 30   # 95%+ — qo'shimcha +30$
        
        # 3) KAROBKA
        if not has_box:
            # Modelga qarab 30-80$ tushadi
            if base_price > 800:
                base_price -= 80
            elif base_price > 500:
                base_price -= 60
            elif base_price > 300:
                base_price -= 40
            else:
                base_price -= 30
        
        # 4) REGION
        # LL/A, ZA/A — eng qimmat (default)
        # KH/A, CH/A — arzonroq
        if region in ['kh', 'ch', 'j']:
            base_price -= 15
        
        # 5) XOTIRA (128GB bazaviy, qo'shimcha xotira uchun ustama)
        if memory == '256':
            base_price += 50
        elif memory == '512':
            base_price += 120
        elif memory == '1024':
            base_price += 200
        
        # 6) TASHQI HOLAT tuzatish
        if condition == 'medium':
            base_price = int(base_price * 0.92)  # -8%
        elif condition == 'bad':
            base_price = int(base_price * 0.82)  # -18%
        
        # Minimum narx
        if base_price < 80:
            base_price = 80
        
        # USD -> SO'M (1$ ≈ 12,700 so'm), 100,000 ga yaxlitlash
        price_som = int(base_price * 12700 / 100000) * 100000
        
        # Narx oralig'i ko'rsatish (±5%)
        price_low = int(price_som * 0.95 / 100000) * 100000
        price_high = int(price_som * 1.05 / 100000) * 100000
        
        # Telegram xabar
        try:
            from core.telegram_bot import send_admin_notification
            box_txt = '📦 Bor' if has_box else "❌ Yo'q"
            region_names = {'ll': 'LL/A (AQSh)', 'za': 'ZA/A (Gonkong)', 'kh': 'KH/A (Koreya)', 'ch': 'CH/A (Xitoy)', 'j': 'J/A (Yaponiya)'}
            reg_txt = region_names.get(region, region)
            tier_names = {'A': 'A-Toifa ✨', 'B': 'B-Toifa 👍', 'C': 'C-Toifa ⚠️'}
            msg = (
                f"🧮 <b>NARX KALKULYATORI</b>\n\n"
                f"📱 Model: iPhone {model}\n"
                f"💾 Xotira: {memory} GB\n"
                f"🔋 Batareya: {battery}%\n"
                f"🛠 Holat: {condition}\n"
                f"📦 Karobka: {box_txt}\n"
                f"🌍 Region: {reg_txt}\n"
                f"📊 Toifa: {tier_names.get(tier, tier)}\n\n"
                f"💰 <b>Narx: ~{base_price}$ ({price_som:,.0f} so'm)</b>"
            )
            send_admin_notification(msg)
        except Exception:
            pass
            
        result_text = f"{price_low:,.0f} – {price_high:,.0f}".replace(',', ' ')
        
        return render(request, 'phones/calculator.html', {
            'result': result_text,
            'result_usd': base_price,
            'tier': tier,
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

class BookPhoneView(View):
    def post(self, request, pk):
        phone = get_object_or_404(Phone, pk=pk)
        if not phone.is_available:
            messages.error(request, "Afsuski, bu telefon allaqachon bron qilingan.")
            return redirect('phones:detail', pk=pk)
            
        from django.utils import timezone
        phone.is_booked = True
        phone.booked_at = timezone.now()
        phone.booked_by = "Web Mijoz"
        phone.save()
        messages.success(request, "✅ Telefon 2 kunga muvaffaqiyatli bron qilindi!")
        
        # Admin notification
        try:
            from core.telegram_bot import send_admin_notification
            msg = f"📌 <b>Yangi Bron!</b>\n\n📱 Model: {phone.get_model_name_display()}\n💰 Narxi: {int(phone.price):,.0f} so'm\n🆔 ID: {phone.id}"
            send_admin_notification(msg)
        except Exception:
            pass
            
        return redirect('phones:detail', pk=pk)
