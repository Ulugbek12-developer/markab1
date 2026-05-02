from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from strings import STRINGS

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
    builder.row(KeyboardButton(text=s['btn_sell']), KeyboardButton(text=s['btn_buy']))
    builder.row(KeyboardButton(text=s['btn_price']), KeyboardButton(text=s['btn_branches']))
    builder.row(
        KeyboardButton(text=s['btn_miniapp'], web_app=WebAppInfo(url="https://markab2.pythonanywhere.com/")),
        KeyboardButton(text=s['btn_help'])
    )
    builder.row(KeyboardButton(text=s['btn_admin']))
    return builder.as_markup(resize_keyboard=True)

def get_admin_panel_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_add_product']), KeyboardButton(text=s['btn_manage_branches']))
    builder.row(KeyboardButton(text=s['btn_delete_product']), KeyboardButton(text=s['btn_exit']))
    return builder.as_markup(resize_keyboard=True)

def get_admin_branch_mgmt_keyboard(lang):
    s = STRINGS[lang]
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=s['btn_add_branch']), KeyboardButton(text=s['btn_delete_branch']))
    builder.row(KeyboardButton(text=s['btn_back_to_admin']))
    return builder.as_markup(resize_keyboard=True)

def get_iphone_models_keyboard(lang):
    s = STRINGS[lang]
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
        builder.row(KeyboardButton(text="Yangi"), KeyboardButton(text="Ideal"))
        builder.row(KeyboardButton(text="Yaxshi"), KeyboardButton(text="Ta'mir talab"))
    else:
        builder.row(KeyboardButton(text="Новый"), KeyboardButton(text="Идеал"))
        builder.row(KeyboardButton(text="Хороший"), KeyboardButton(text="Требует ремонта"))
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
        builder.row(KeyboardButton(text="📦 Karobka hujjati bor"), KeyboardButton(text="🚫 Karobka hujjati yo'q"))
    else:
        builder.row(KeyboardButton(text="📦 Коробка/Документы есть"), KeyboardButton(text="🚫 Коробки/Документов нет"))
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
