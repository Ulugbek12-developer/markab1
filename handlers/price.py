from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import PricePhone
from keyboards import (
    get_iphone_models_keyboard, get_battery_range_keyboard, get_memory_keyboard,
    get_condition_keyboard, get_region_keyboard, get_box_keyboard,
    get_main_menu, get_back_keyboard, get_price_admin_keyboard
)
from database import add_price_request
from config import config

from database import add_price_request, get_user_language
from config import config
from strings import STRINGS

router = Router()

BASE_PRICES = {
    "iPhone 11": 300, "iPhone 11 Pro": 400, "iPhone 11 Pro Max": 450,
    "iPhone 12": 400, "iPhone 12 Pro": 500, "iPhone 12 Pro Max": 550,
    "iPhone 13": 500, "iPhone 13 Pro": 650, "iPhone 13 Pro Max": 750,
    "iPhone 14": 650, "iPhone 14 Pro": 850, "iPhone 14 Pro Max": 950,
    "iPhone 15": 800, "iPhone 15 Pro": 1050, "iPhone 15 Pro Max": 1150,
    "iPhone 16": 1000, "iPhone 16 Pro": 1300, "iPhone 16 Pro Max": 1450,
}

def calculate_price(data):
    model = data.get('model', "")
    base = BASE_PRICES.get(model, 500)
    
    # Memory adjustments
    storage = data.get('storage', "128GB")
    if "256" in storage: base += 50
    elif "512" in storage: base += 100
    elif "1TB" in storage: base += 200
    
    # Battery adjustments
    battery = data.get('battery_range', "90-100")
    if "70-80" in battery: base -= 30
    elif "60-70" in battery: base -= 60
    
    # Condition
    cond = data.get('condition', "").lower()
    if "yaxshi" in cond or "хороший" in cond: base -= 50
    elif "ta'mir" in cond or "ремонта" in cond: base -= 150
    
    return round(base / 100, 1) # Return in millions

@router.message(F.text.in_(["💰 Narxlatish", "💰 Оценка"]))
async def start_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(PricePhone.model)
    await message.answer(STRINGS[lang]['prompt_price_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))

@router.message(PricePhone.model)
async def process_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
        return
    
    await state.update_data(model=message.text)
    await state.set_state(PricePhone.photos)
    await state.update_data(photos=[])
    await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(PricePhone.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    await state.set_state(PricePhone.battery_range)
    await message.answer(STRINGS[lang]['prompt_price_battery'], parse_mode="HTML", reply_markup=get_battery_range_keyboard(lang))

@router.message(PricePhone.battery_range)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.model)
        await message.answer(STRINGS[lang]['prompt_price_model'], reply_markup=get_iphone_models_keyboard(lang))
        return

    if message.text in ["Boshqa", "Другое"]:
        await state.set_state(PricePhone.manual_battery)
        await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    await state.update_data(battery_range=message.text)
    await state.set_state(PricePhone.memory)
    await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))

@router.message(PricePhone.manual_battery)
async def process_manual_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.battery_range)
        await message.answer(STRINGS[lang]['prompt_price_battery'], reply_markup=get_battery_range_keyboard(lang))
        return
    
    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer(STRINGS[lang]['err_battery'])
        return
        
    await state.update_data(battery_range=message.text)
    await state.set_state(PricePhone.memory)
    await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))

@router.message(PricePhone.memory)
async def process_memory(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.battery_range)
        await message.answer(STRINGS[lang]['prompt_price_battery'], reply_markup=get_battery_range_keyboard(lang))
        return
    
    await state.update_data(storage=message.text)
    await state.set_state(PricePhone.condition)
    await message.answer(STRINGS[lang]['prompt_price_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))

@router.message(PricePhone.condition)
async def process_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.memory)
        await message.answer(STRINGS[lang]['prompt_price_memory'], reply_markup=get_memory_keyboard(lang))
        return
    
    await state.update_data(condition=message.text)
    await state.set_state(PricePhone.region)
    await message.answer(STRINGS[lang]['prompt_price_region'], parse_mode="HTML", reply_markup=get_region_keyboard(lang))

@router.message(PricePhone.region)
async def process_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.condition)
        await message.answer(STRINGS[lang]['prompt_price_condition'], reply_markup=get_condition_keyboard(lang))
        return
    
    await state.update_data(region=message.text)
    await state.set_state(PricePhone.box)
    await message.answer(STRINGS[lang]['prompt_price_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))

@router.message(PricePhone.box)
async def process_box(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(PricePhone.region)
        await message.answer(STRINGS[lang]['prompt_price_region'], reply_markup=get_region_keyboard(lang))
        return
    
    await state.update_data(box=message.text)
    data = await state.get_data()
    recommended_price = calculate_price(data)
    s = STRINGS[lang]
    
    username = message.from_user.username
    user_info = f" (@{username})" if username else ""
    
    summary_for_admin = (
        f"👤 <b>Mijoz:</b> <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>{user_info}\n"
        f"📱 <b>{s['lbl_model']}:</b> {data['model']}\n"
        f"💾 <b>{s['lbl_memory']}:</b> {data['storage']}\n"
        f"🔋 <b>{s['lbl_battery']}:</b> {data['battery_range']}%\n"
        f"📦 <b>{s['lbl_box']}:</b> {data['box']}\n"
        f"🌍 <b>{s['lbl_region']}:</b> {data['region']}\n"
        f"📐 <b>Tavsiya etilgan narx:</b> {recommended_price} mln so'm"
    )
    
    # Send to Admin
    data['user_id'] = message.from_user.id
    data['calculated_price'] = str(recommended_price)
    req_id = await add_price_request(data)
    
    if config.ADMIN_ID:
        admin_text = f"🆕 <b>YANGI NARXLASH SO'ROVI (ID: {req_id})</b>\n\n" + summary_for_admin
        await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_text, parse_mode="HTML", reply_markup=get_price_admin_keyboard(req_id, lang))

    await message.answer(s['price_success'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    await state.clear()
