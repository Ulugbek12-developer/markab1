from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📱 Telefon sotish"), KeyboardButton(text="🛍 Telefon sotib olish"))
    builder.row(KeyboardButton(text="💰 Narxlatish"), KeyboardButton(text="🏢 Bizning filiallar"))
    builder.row(
        KeyboardButton(text="🌐 Mini App", web_app=WebAppInfo(url="https://markab.pythonanywhere.com/")),
        KeyboardButton(text="ℹ️ Ma'lumot/Yordam")
    )
    builder.row(KeyboardButton(text="🔐 Admin Panel"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_panel_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Mahsulot qo'shish"), KeyboardButton(text="🏢 Filiallarni boshqarish"))
    builder.row(KeyboardButton(text="🗑 Mahsulotni o'chirish"), KeyboardButton(text="⬅️ Chiqish"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_branch_mgmt_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➕ Yangi filial qo'shish"), KeyboardButton(text="❌ Filialni o'chirish"))
    builder.row(KeyboardButton(text="⬅️ Admin menyuga qaytish"))
    return builder.as_markup(resize_keyboard=True)

def get_iphone_models_keyboard():
    builder = ReplyKeyboardBuilder()
    models = ["iPhone 11", "iPhone 11 Pro", "iPhone 11 Pro Max",
              "iPhone 12", "iPhone 12 Pro", "iPhone 12 Pro Max",
              "iPhone 13", "iPhone 13 Pro", "iPhone 13 Pro Max",
              "iPhone 14", "iPhone 14 Pro", "iPhone 14 Pro Max",
              "iPhone 15", "iPhone 15 Pro", "iPhone 15 Pro Max",
              "iPhone 16", "iPhone 16 Pro", "iPhone 16 Pro Max",
              "iPhone 17", "iPhone 17 Pro", "iPhone 17 Pro Max"]
    for i in range(0, len(models), 3):
        builder.row(*[KeyboardButton(text=m) for m in models[i:i+3]])
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_memory_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="64GB"), KeyboardButton(text="128GB"))
    builder.row(KeyboardButton(text="256GB"), KeyboardButton(text="512GB"))
    builder.row(KeyboardButton(text="1TB"), KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_condition_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Yangi"), KeyboardButton(text="Ideal"))
    builder.row(KeyboardButton(text="Yaxshi"), KeyboardButton(text="Ta'mir talab"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_region_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="LLA"), KeyboardButton(text="ZP"), KeyboardButton(text="CH"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_box_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📦 Karobka hujjati bor"), KeyboardButton(text="🚫 Karobka hujjati yo'q"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_battery_range_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="60-70"), KeyboardButton(text="70-80"))
    builder.row(KeyboardButton(text="80-90"), KeyboardButton(text="90-100"))
    builder.row(KeyboardButton(text="Boshqa"), KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_branches_keyboard(branches):
    builder = ReplyKeyboardBuilder()
    for b in branches:
        name = b['name'] if hasattr(b, '__getitem__') and 'name' in b.keys() else b
        builder.row(KeyboardButton(text=name))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_contact_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="📞 Raqamni ulashish", request_contact=True))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_confirm_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="✅ Tasdiqlash"), KeyboardButton(text="❌ Bekor qilish"))
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_back_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="⬅️ Orqaga"))
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard(ad_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{ad_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{ad_id}")
    )
    return builder.as_markup()

def get_price_admin_keyboard(req_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ Narx yozish", callback_data=f"setprice_{req_id}"))
    return builder.as_markup()
