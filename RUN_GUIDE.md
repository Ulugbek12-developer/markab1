# 🚀 Django Marketplace Ishga tushirish qo'llanmasi

Loyiha to'liq **Django** (Python) stackida, premium modern dizayn bilan tayyorlandi.

---

## 1. Dasturni sozlash

1.  **Virtual muhitni ishga tushiring:**
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
2.  **Kutubxonalarni o'rnating:**
    ```powershell
    pip install -r requirements.txt
    ```
3.  **Ma'lumotlar bazasini yangilang:**
    ```powershell
    python manage.py makemigrations
    python manage.py migrate
    ```
4.  **Kategoriyalarni yarating:**
    ```powershell
    python seed_django.py
    ```

---

## 2. Ishga tushirish

1.  **Veb-saytni ishga tushirish:**
    ```powershell
    python manage.py runserver
    ```
    Sayt `http://127.0.0.1:8000` manzilida ishlaydi.

2.  **Telegram Botni ishga tushirish:**
    ```powershell
    python main.py
    ```

---

## ✨ Yangiliklar

-   **Premium Dizayn**: Tailwind CSS va "Milky Light" stilidagi zamonaviy interfeys.
-   **Kategoriyalar**: Endi nafaqat telefonlar, balki noutbuk va aksessuarlar ham bor.
-   **Saralanganlar**: Foydalanuvchilar o'zlariga yoqqan e'lonlarni saqlab qo'yishlari mumkin.
-   **Oson Sotish**: Foydalanuvchi uchun qulay e'lon berish formasi.
-   **Bot Integratsiyasi**: Botdagi tugmalar bevosita saytning kerakli bo'limlariga (Sotish, Narxlash) olib boradi.

---

## 💡 Muhim
Admin panelga kirish uchun `python manage.py createsuperuser` buyrug'i orqali admin yarating.
Saytni Telegramda Mini App sifatida tekshirish uchun **ngrok** ishlatishni unutmang.
