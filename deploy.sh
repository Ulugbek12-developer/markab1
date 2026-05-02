#!/bin/bash
# ============================================================
# Markab Electronics - PythonAnywhere Deploy Script
# Ishlatish: bash deploy.sh
# ============================================================

echo "🚀 Markab Electronics deployment boshlanmoqda..."
echo "=================================================="

# 1. Git pull
echo "📥 [1/5] Yangi kodlarni yuklab olish..."
git pull origin main
if [ $? -ne 0 ]; then
    echo "❌ git pull xatosi! Network yoki branch nomini tekshiring."
    exit 1
fi
echo "✅ Kod yangilandi."

# 2. Install requirements (if new packages added)
echo "📦 [2/5] Pakketlar tekshirilmoqda..."
pip install -r requirements.txt -q
echo "✅ Pakketlar tayyor."

# 3. Run Django migrations
echo "🗃️ [3/5] Ma'lumotlar bazasi yangilanmoqda..."
python manage.py migrate --no-input
echo "✅ Migrations bajarildi."

# 4. Collect static files
echo "🎨 [4/5] Statik fayllar yig'ilmoqda..."
python manage.py collectstatic --no-input -v 0
echo "✅ Static files tayyor."

# 5. Reload web app via PythonAnywhere API (touch WSGI file)
echo "🔄 [5/5] Web app qayta yuklanmoqda..."
WSGI_FILE=$(find /var/www -name "*.wsgi" 2>/dev/null | head -1)
if [ -n "$WSGI_FILE" ]; then
    touch "$WSGI_FILE"
    echo "✅ WSGI fayl tegildi: $WSGI_FILE"
else
    echo "⚠️ WSGI fayl topilmadi. PythonAnywhere dashboard'dan qo'lda Reload qiling."
fi

echo ""
echo "=================================================="
echo "🎉 Deployment muvaffaqiyatli yakunlandi!"
echo "🌐 Saytingiz: https://markab.pythonanywhere.com"
echo "=================================================="
