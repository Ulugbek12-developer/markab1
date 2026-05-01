# PythonAnywhere Deployment Guide

Bu qo'llanma loyihangizni PythonAnywhere hostingiga muvaffaqiyatli yuklash va ishga tushirishga yordam beradi.

## 1. Fayllarni yuklash
1. Loyihangizni `.zip` qilib arxivlang ( `.venv`, `__pycache__` va `.git` papkalarisiz).
2. PythonAnywhere'da **Files** bo'limiga o'ting va arxivni yuklang.
3. **Consoles** bo'limida yangi Bash konsol oching va arxivni oching:
   ```bash
   unzip isell.zip
   ```

## 2. Virtual muhit yaratish
Konsolda quyidagi buyruqlarni bajaring:
```bash
mkvirtualenv venv --python=python3.10
pip install -r requirements.txt
```

## 3. Web App sozlash
1. **Web** tabiga o'ting va **Add a new web app** tugmasini bosing.
2. **Manual Configuration** -> **Python 3.10** ni tanlang.
3. **Code** bo'limida:
   - **Source code**: `/home/username/isell`
   - **Working directory**: `/home/username/isell`
   - **Virtualenv**: `/home/username/.virtualenvs/venv`
4. **WSGI configuration file** ni tahrirlang:
   ```python
   import os
   import sys

   path = '/home/username/isell'
   if path not in sys.path:
       sys.path.append(path)

   os.environ['DJANGO_SETTINGS_MODULE'] = 'core.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

## 4. Statik fayllar va Ma'lumotlar bazasi
Konsolda:
```bash
python manage.py collectstatic
python manage.py migrate
```
**Web** tabida **Static files** bo'limiga:
- URL: `/static/` -> Path: `/home/username/isell/staticfiles/`
- URL: `/media/` -> Path: `/home/username/isell/media/`

## 5. Telegram Botni ishga tushirish
PythonAnywhere'da bot doimiy ishlashi uchun **Tasks** bo'limidan foydalaning (Paid account bo'lsa "Always-on tasks", bo'lmasa "Scheduled Tasks").
Buyruq:
```bash
/home/username/.virtualenvs/venv/bin/python /home/username/isell/main.py
```

> [!TIP]
> Agar bot ishlamasa, konsolda `python main.py` qilib xatolikni tekshirib ko'ring. Kanalga botni **Admin** qilib qo'shishni unutmang!
