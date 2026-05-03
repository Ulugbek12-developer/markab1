from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from strings import STRINGS

IPHONE_COLORS = {
    "iPhone 11": ["Black", "White", "Green", "Yellow", "Purple", "Red"],
    "iPhone 11 Pro": ["Midnight Green", "Space Gray", "Silver", "Gold"],
    "iPhone 11 Pro Max": ["Midnight Green", "Space Gray", "Silver", "Gold"],
    "iPhone 12": ["Black", "White", "Red", "Green", "Blue", "Purple"],
    "iPhone 12 Pro": ["Graphite", "Silver", "Gold", "Pacific Blue"],
    "iPhone 12 Pro Max": ["Graphite", "Silver", "Gold", "Pacific Blue"],
    "iPhone 13": ["Starlight", "Midnight", "Blue", "Pink", "Red", "Green"],
    "iPhone 13 Pro": ["Graphite", "Silver", "Gold", "Sierra Blue", "Alpine Green"],
    "iPhone 13 Pro Max": ["Graphite", "Silver", "Gold", "Sierra Blue", "Alpine Green"],
    "iPhone 14": ["Midnight", "Starlight", "Blue", "Purple", "Red", "Yellow"],
    "iPhone 14 Pro": ["Space Black", "Silver", "Gold", "Deep Purple"],
    "iPhone 14 Pro Max": ["Space Black", "Silver", "Gold", "Deep Purple"],
    "iPhone 15": ["Black", "Blue", "Green", "Yellow", "Pink"],
    "iPhone 15 Pro": ["Black Titanium", "White Titanium", "Blue Titanium", "Natural Titanium"],
    "iPhone 15 Pro Max": ["Black Titanium", "White Titanium", "Blue Titanium", "Natural Titanium"],
    "iPhone 16": ["Black", "White", "Pink", "Teal", "Ultramarine"],
    "iPhone 16 Pro": ["Black Titanium", "White Titanium", "Natural Titanium", "Desert Titanium"],
    "iPhone 16 Pro Max": ["Black Titanium", "White Titanium", "Natural Titanium", "Desert Titanium"],
    "iPhone 17 Pro Max": ["Orange", "Blue", "Silver"]
}

def get_language_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇺🇿 O'zbek tili", callback_data="lang_uz"),
        InlineKeyboardButton(text="🇷🇺 Русский язык", callback_data="lang_ru")
    )
    return builder.as_markup()

def get_subscription_keyboard(lang):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=STRINGS[lang]['btn_sub'], url="https://t.me/markab_electronics"))
    builder.row(InlineKeyboardButton(text=STRINGS[lang]['btn_check'], callback_data="check_sub"))
    return builder.as_markup()

def get_main_menu(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=s['btn_sell']), 
        KeyboardButton(text=s['btn_buy'])
    )
    builder.row(
        KeyboardButton(text=s['btn_price']), 
        KeyboardButton(text=s['btn_branches'])
    )
    builder.row(
        KeyboardButton(text=s['btn_miniapp'], web_app=WebAppInfo(url="https://markabstore.pythonanywhere.com")),
        KeyboardButton(text=s['btn_help'])
    )
    builder.row(KeyboardButton(text=s['btn_admin']))
    return builder.as_markup(resize_keyboard=True)

def get_choice_keyboard(lang, action_type):
    s = STRINGS[lang]
    base_url = "https://markabstore.pythonanywhere.com"
    urls = {
        'sell': f"{base_url}/sell/",
        'buy': f"{base_url}/",
        'price': f"{base_url}/price/"
    }
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_continue_bot']))
    builder.row(KeyboardButton(text=s['btn_open_miniapp'], web_app=WebAppInfo(url=urls.get(action_type, base_url))))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_admin_panel_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_add_product']), KeyboardButton(text=s['btn_manage_branches']))
    builder.row(KeyboardButton(text=s['btn_delete_product']), KeyboardButton(text=s['btn_stats']))
    builder.row(KeyboardButton(text=s['btn_exit']))
    return builder.as_markup(resize_keyboard=True)

def get_admin_branch_mgmt_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_add_branch']), KeyboardButton(text=s['btn_delete_branch']))
    builder.row(KeyboardButton(text=s['btn_back_to_admin']))
    return builder.as_markup(resize_keyboard=True)

REPLACED_PARTS = [
    ("batareya", "part_battery", "🔋"),
    ("ekran", "part_display", "📱"),
    ("orqa_qopqoq", "part_glass", "🔲"),
    ("kamera", "part_camera", "📷"),
    ("dinamik", "part_audio", "🔊"),
    ("tugmalar", "part_buttons", "⚙️"),
    ("boshqa", "part_other", "🔧"),
    ("almashtirilmagan", "part_none", "✅"),
]

DEFECTS_LIST = [
    ("face_id", "defect_faceid", "🔓"),
    ("true_tone", "defect_truetone", "🎨"),
    ("old_kamera", "defect_camera_front", "📷"),
    ("asosiy_kamera", "defect_camera_back", "📸"),
    ("dinamiklar", "defect_audio", "🔊"),
    ("mikrofon", "defect_mic", "🎤"),
    ("vibro", "defect_vibro", "📳"),
    ("wifi_bt", "defect_wifi", "📶"),
    ("gps", "defect_gps", "📍"),
    ("nfc", "defect_nfc", "💳"),
    ("hammasi_ishlaydi", "defect_none", "✅"),
]

def get_replaced_parts_keyboard(selected_keys, lang='uz'):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    
    for key, string_key, icon in REPLACED_PARTS:
        label = s[string_key]
        display_label = f"✅ {icon} {label}" if key in selected_keys else f"{icon} {label}"
        builder.add(KeyboardButton(text=display_label))
    
    builder.adjust(2)
    builder.row(KeyboardButton(text=s['btn_continue']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_defects_keyboard(selected_keys, lang='uz'):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    
    for key, string_key, icon in DEFECTS_LIST:
        label = s[string_key]
        display_label = f"✅ {icon} {label}" if key in selected_keys else f"{icon} {label}"
        builder.add(KeyboardButton(text=display_label))
    
    builder.adjust(2)
    builder.row(KeyboardButton(text=s['btn_continue']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_yes_no_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_yes']), KeyboardButton(text=s['btn_no']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)


def get_iphone_models_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    models = sorted(list(IPHONE_COLORS.keys()), reverse=True)
    for i in range(0, len(models), 3):
        builder.row(*[KeyboardButton(text=m) for m in models[i:i+3]])
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_color_keyboard(model, lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    colors = IPHONE_COLORS.get(model, ["Black", "White", "Gold", "Silver"])
    for i in range(0, len(colors), 2):
        builder.row(*[KeyboardButton(text=c) for c in colors[i:i+2]])
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_memory_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="64GB"), KeyboardButton(text="128GB"))
    builder.row(KeyboardButton(text="256GB"), KeyboardButton(text="512GB"))
    builder.row(KeyboardButton(text="1TB"), KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_condition_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    if lang == 'uz':
        builder.row(KeyboardButton(text="🆕 Yangi (Upakovka)"), KeyboardButton(text="✨ Ideal"))
        builder.row(KeyboardButton(text="👍 Yaxshi"), KeyboardButton(text="🛠 Ta'mir talab"))
    else:
        builder.row(KeyboardButton(text="🆕 Новый"), KeyboardButton(text="✨ Идеал"))
        builder.row(KeyboardButton(text="👍 Хороший"), KeyboardButton(text="🛠 Требует ремонта"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_region_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="LL/A (AQSh)"), KeyboardButton(text="ZA/A (Gonkong)"))
    builder.row(KeyboardButton(text="KH/A (Koreya)"), KeyboardButton(text="CH/A (Xitoy)"))
    builder.row(KeyboardButton(text="J/A (Yaponiya)"), KeyboardButton(text="Boshqa"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_box_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    if lang == 'uz':
        builder.row(KeyboardButton(text="📦 Bor"), KeyboardButton(text="🚫 Yo'q"))
    else:
        builder.row(KeyboardButton(text="📦 Есть"), KeyboardButton(text="🚫 Нет"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_opened_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    if lang == 'uz':
        builder.row(KeyboardButton(text="🛠 Ha, ochilgan"), KeyboardButton(text="✅ Yo'q, ochilmagan"))
    else:
        builder.row(KeyboardButton(text="🛠 Да, вскрывался"), KeyboardButton(text="✅ Нет, не вскрывался"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_continue_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="➡️ Davom etish" if lang == 'uz' else "➡️ Продолжить"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_confirm_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_confirm']), KeyboardButton(text=s['btn_cancel']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_back_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_branches_keyboard(branches, lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    for b in branches:
        name = b['name'] if hasattr(b, '__getitem__') and 'name' in b.keys() else b
        builder.row(KeyboardButton(text=name))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_contact_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_share_contact'], request_contact=True))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_admin_keyboard(ad_id: int, lang):
    s = STRINGS[lang]
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=s['btn_approve'], callback_data=f"approve_{ad_id}"),
        InlineKeyboardButton(text=s['btn_counter'], callback_data=f"counter_{ad_id}"),
        InlineKeyboardButton(text=s['btn_reject'], callback_data=f"reject_{ad_id}")
    )
    return builder.as_markup()

def get_price_admin_keyboard(req_id: int, lang):
    s = STRINGS[lang]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=s['btn_set_price'], callback_data=f"setprice_{req_id}"))
    return builder.as_markup()

def get_user_counter_response_keyboard(ad_id: int):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Roziman", callback_data=f"user_agree_{ad_id}"),
        InlineKeyboardButton(text="❌ Noroziman", callback_data=f"user_disagree_{ad_id}")
    )
    return builder.as_markup()

def get_payment_type_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_cash']), KeyboardButton(text=s['btn_installment']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_location_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_city']))
    builder.row(KeyboardButton(text=s['btn_region']))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_installment_plan_keyboard(m3, m6, m12, lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=f"3 oy - {m3:,.0f} so'm"), 
        KeyboardButton(text=f"6 oy - {m6:,.0f} so'm")
    )
    builder.row(KeyboardButton(text=f"12 oy - {m12:,.0f} so'm"))
    builder.row(KeyboardButton(text=s['btn_back']))
    return builder.as_markup(resize_keyboard=True)

def get_order_admin_keyboard(listing_id: int, lang):
    s = STRINGS[lang]
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Bron qilish (48s)", callback_data=f"book_{listing_id}"),
        InlineKeyboardButton(text="❌ Rad etish", callback_data=f"rejectorder_{listing_id}")
    )
    return builder.as_markup()
