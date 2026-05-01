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

router = Router()

BASE_PRICES = {
    "iPhone 11": (2.5, 3.5), "iPhone 11 Pro": (3, 4), "iPhone 11 Pro Max": (3.5, 4.5),
    "iPhone 12": (3.5, 4.5), "iPhone 12 Pro": (4, 5.5), "iPhone 12 Pro Max": (5, 6.5),
    "iPhone 13": (4.5, 5.5), "iPhone 13 Pro": (5.5, 6.5), "iPhone 13 Pro Max": (6, 7.5),
    "iPhone 14": (5.5, 6.5), "iPhone 14 Pro": (6.5, 8), "iPhone 14 Pro Max": (7.5, 9),
    "iPhone 15": (7, 8.5), "iPhone 15 Pro": (8.5, 10), "iPhone 15 Pro Max": (9, 11),
    "iPhone 16": (8, 10), "iPhone 16 Pro": (10, 12), "iPhone 16 Pro Max": (11, 14),
    "iPhone 17": (9, 11), "iPhone 17 Pro": (13, 16), "iPhone 17 Pro Max": (13, 18),
}

def calculate_price(data):
    model = data.get('model')
    battery = data.get('battery_range')
    storage = data.get('storage')
    condition = data.get('condition')
    region = data.get('region')
    box = data.get('box')

    if model not in BASE_PRICES:
        return "Noma'lum"

    min_p, max_p = BASE_PRICES[model]
    # Use average for calculation
    price = (min_p + max_p) / 2
    
    # Battery adjustments
    try:
        val = int(battery) if battery.isdigit() else int(battery.split("-")[0])
        if 80 <= val < 90: price -= 0.3
        elif 70 <= val < 80: price -= 0.5
        elif val < 70: price -= 0.8
    except Exception:
        pass
    
    # Box
    if "bor" in box.lower(): price += 0.3
    
    # Storage
    if storage == "256GB": price += 0.3
    elif storage == "512GB": price += 0.6
    elif storage == "1TB": price += 1.0 # Assumption for 1TB
    
    # Condition
    if condition == "Yaxshi": price -= 0.3
    elif "tamir" in condition.lower(): price -= 0.7
    
    # Region
    if region == "CH": price -= 0.2
    elif region == "LLA": price += 0.2
    
    return round(price, 1)

@router.message(F.text == "💰 Narxlatish")
async def start_price(message: Message, state: FSMContext):
    await state.set_state(PricePhone.model)
    await message.answer("📲 <b>Qaysi iPhone modelini narxlatmoqchisiz?</b>", parse_mode="HTML", reply_markup=get_iphone_models_keyboard())

@router.message(PricePhone.model)
async def process_model(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyu", reply_markup=get_main_menu())
        return
    
    await state.update_data(model=message.text)
    await state.set_state(PricePhone.photos)
    await state.update_data(photos=[])
    await message.answer("📸 <b>Telefonning 1 ta sifatli rasmini yuboring:</b>", parse_mode="HTML", reply_markup=get_back_keyboard())

@router.message(PricePhone.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    await state.set_state(PricePhone.battery_range)
    await message.answer("🔋 <b>Batareya yomkostini tanlang:</b>", parse_mode="HTML", reply_markup=get_battery_range_keyboard())

@router.message(PricePhone.battery_range)
async def process_battery(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.model)
        await message.answer("📱 Modelni tanlang:", reply_markup=get_iphone_models_keyboard())
        return

    if message.text == "Boshqa":
        await state.set_state(PricePhone.manual_battery)
        await message.answer("🔋 <b>Batareya yomkostini raqamda kiriting (masalan: 88):</b>", parse_mode="HTML", reply_markup=get_back_keyboard())
        return

    await state.update_data(battery_range=message.text)
    await state.set_state(PricePhone.memory)
    await message.answer("💾 <b>Xotira hajmini tanlang:</b>", parse_mode="HTML", reply_markup=get_memory_keyboard())

@router.message(PricePhone.manual_battery)
async def process_manual_battery(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.battery_range)
        await message.answer("🔋 Batareya yomkostini tanlang:", reply_markup=get_battery_range_keyboard())
        return
    
    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer("❌ Iltimos, haqiqiy foiz kiriting (1-100):")
        return
        
    await state.update_data(battery_range=message.text)
    await state.set_state(PricePhone.memory)
    await message.answer("💾 <b>Xotira hajmini tanlang:</b>", parse_mode="HTML", reply_markup=get_memory_keyboard())

@router.message(PricePhone.memory)
async def process_memory(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.battery_range)
        await message.answer("🔋 Batareya yomkostini tanlang:", reply_markup=get_battery_range_keyboard())
        return
    
    await state.update_data(storage=message.text)
    await state.set_state(PricePhone.condition)
    await message.answer("🛠 <b>Telefon holatini tanlang:</b>", parse_mode="HTML", reply_markup=get_condition_keyboard())

@router.message(PricePhone.condition)
async def process_condition(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.memory)
        await message.answer("💾 Xotira hajmini tanlang:", reply_markup=get_memory_keyboard())
        return
    
    await state.update_data(condition=message.text)
    await state.set_state(PricePhone.region)
    await message.answer("🌍 <b>Regionni tanlang:</b>", parse_mode="HTML", reply_markup=get_region_keyboard())

@router.message(PricePhone.region)
async def process_region(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.condition)
        await message.answer("🛠 Telefon holatini tanlang:", reply_markup=get_condition_keyboard())
        return
    
    await state.update_data(region=message.text)
    await state.set_state(PricePhone.box)
    await message.answer("📦 <b>Karobka va hujjati bormi?</b>", parse_mode="HTML", reply_markup=get_box_keyboard())

@router.message(PricePhone.box)
async def process_box(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(PricePhone.region)
        await message.answer("🌍 Regionni tanlang:", reply_markup=get_region_keyboard())
        return
    
    await state.update_data(box=message.text)
    data = await state.get_data()
    recommended_price = calculate_price(data)
    
    summary_for_admin = (
        f"📱 <b>Model:</b> {data['model']}\n"
        f"💾 <b>Xotira:</b> {data['storage']}\n"
        f"🔋 <b>Batareya:</b> {data['battery_range']}%\n"
        f"📦 <b>Karobka:</b> {data['box']}\n"
        f"🌍 <b>Region:</b> {data['region']}\n"
        f"📐 <b>Tavsiya etilgan narx:</b> {recommended_price} mln so'm"
    )
    
    # Send to Admin
    data['user_id'] = message.from_user.id
    data['calculated_price'] = str(recommended_price)
    req_id = await add_price_request(data)
    
    if config.ADMIN_ID:
        admin_text = f"🆕 <b>YANGI NARXLASH SO'ROVI (ID: {req_id})</b>\n\n" + summary_for_admin
        await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_text, parse_mode="HTML", reply_markup=get_price_admin_keyboard(req_id))

    await message.answer(
        "✅ <b>Ma'lumotlar qabul qilindi!</b>\n\n"
        "⏳ Mutaxassislarimiz telefoningiz holatini o'rganib chiqib, tez orada sizga aniq narxni yuborishadi.\n\n"
        "🔔 <i>Iltimos, bot xabarlarini kuting!</i>",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )
    await state.clear()
