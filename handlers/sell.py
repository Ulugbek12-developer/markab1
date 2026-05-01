from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import SellPhone
from keyboards import (
    get_iphone_models_keyboard, get_memory_keyboard, get_condition_keyboard, 
    get_contact_keyboard, get_confirm_keyboard, get_back_keyboard, get_main_menu,
    get_admin_keyboard, get_region_keyboard, get_box_keyboard
)
from database import add_ad
from config import config

router = Router()

@router.message(F.text == "📱 Telefon sotish")
async def start_sell(message: Message, state: FSMContext):
    await state.set_state(SellPhone.model)
    await message.answer("📲 <b>Sotmoqchi bo'lgan iPhone modelini tanlang:</b>", parse_mode="HTML", reply_markup=get_iphone_models_keyboard())

@router.message(SellPhone.model)
async def process_model(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Bosh sahifa", reply_markup=get_main_menu())
        return
    
    await state.update_data(model=message.text)
    await state.set_state(SellPhone.photos)
    await state.update_data(photos=[])
    await message.answer("📸 <b>Telefonning 1 ta sifatli rasmini yuklang:</b>", parse_mode="HTML", reply_markup=get_back_keyboard())

@router.message(SellPhone.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    await state.set_state(SellPhone.battery)
    await message.answer("🔋 <b>Batareya yomkostini kiriting (% da, masalan: 88):</b>", parse_mode="HTML", reply_markup=get_back_keyboard())

@router.message(SellPhone.battery)
async def process_battery(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.model)
        await message.answer("📲 iPhone modelini tanlang:", reply_markup=get_iphone_models_keyboard())
        return

    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer("❌ Iltimos, haqiqiy foiz kiriting (1-100):")
        return

    await state.update_data(battery=message.text)
    await state.set_state(SellPhone.memory)
    await message.answer("💾 <b>Xotira hajmini tanlang:</b>", parse_mode="HTML", reply_markup=get_memory_keyboard())

@router.message(SellPhone.memory)
async def process_memory(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.battery)
        await message.answer("🔋 Batareya yomkostini kiriting:", reply_markup=get_back_keyboard())
        return

    await state.update_data(memory=message.text, storage=message.text) # store both for compatibility
    await state.set_state(SellPhone.condition)
    await message.answer("🛠 <b>Telefon holatini tanlang:</b>", parse_mode="HTML", reply_markup=get_condition_keyboard())

@router.message(SellPhone.condition)
async def process_condition(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.memory)
        await message.answer("💾 Xotira hajmini tanlang:", reply_markup=get_memory_keyboard())
        return

    await state.update_data(condition=message.text)
    await state.set_state(SellPhone.region)
    await message.answer("🌍 <b>Telefon regionini tanlang:</b>", parse_mode="HTML", reply_markup=get_region_keyboard())

@router.message(SellPhone.region)
async def process_region(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.condition)
        await message.answer("🛠 Telefon holatini tanlang:", reply_markup=get_condition_keyboard())
        return

    await state.update_data(region=message.text)
    await state.set_state(SellPhone.box)
    await message.answer("📦 <b>Karobka va hujjatlari bormi?</b>", parse_mode="HTML", reply_markup=get_box_keyboard())

@router.message(SellPhone.box)
async def process_box(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.region)
        await message.answer("🌍 Telefon regionini tanlang:", reply_markup=get_region_keyboard())
        return

    await state.update_data(box=message.text)
    await state.set_state(SellPhone.price)
    await message.answer("💰 <b>Sotish narxini kiriting (masalan: 500 yoki 500$):</b>", parse_mode="HTML", reply_markup=get_back_keyboard())

@router.message(SellPhone.price)
async def process_price(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.box)
        await message.answer("📦 Karobka va hujjatlari bormi?", reply_markup=get_box_keyboard())
        return

    await state.update_data(price=message.text)
    await state.set_state(SellPhone.contact)
    await message.answer("📞 <b>Bog'lanish uchun telefon raqamingizni yuboring:</b>", parse_mode="HTML", reply_markup=get_contact_keyboard())

@router.message(SellPhone.contact, F.contact | F.text)
async def process_contact(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.price)
        await message.answer("💰 Sotish narxini kiriting:", reply_markup=get_back_keyboard())
        return

    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=phone)
    
    data = await state.get_data()
    summary = (
        f"<b>📋 E'loningiz ma'lumotlari:</b>\n\n"
        f"📱 <b>Model:</b> {data['model']}\n"
        f"💾 <b>Xotira:</b> {data['memory']}\n"
        f"🔋 <b>Batareya:</b> {data['battery']}%\n"
        f"🛠 <b>Holati:</b> {data['condition']}\n"
        f"🌍 <b>Region:</b> {data['region']}\n"
        f"📦 <b>Karobka:</b> {data['box']}\n"
        f"💰 <b>Narxi:</b> {data['price']}\n"
        f"📞 <b>Aloqa:</b> {data['contact']}\n\n"
        "✨ <i>Barchasi to'g'rimi? Tasdiqlaysizmi?</i>"
    )
    
    await state.set_state(SellPhone.confirm)
    await message.answer_photo(photo=data['photos'][0], caption=summary, parse_mode="HTML", reply_markup=get_confirm_keyboard())

@router.message(SellPhone.confirm)
async def process_confirm(message: Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        data['user_id'] = message.from_user.id
        data['storage'] = data['memory']
        ad_id = await add_ad(data)
        
        if config.ADMIN_ID:
            admin_summary = f"🆕 <b>YANGI E'LON (ID: {ad_id})</b>\n\nUser: {message.from_user.full_name}\n" + \
                            f"Model: {data['model']}\nHotira: {data['memory']}\nYomkost: {data['battery']}%\n" + \
                            f"Narxi: {data['price']}\nAloqa: {data['contact']}"
            await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_summary, reply_markup=get_admin_keyboard(ad_id), parse_mode="HTML")

        await message.answer("🎉 <b>Muvaffaqiyatli!</b>\n\nAdmin tasdiqlashi bilan e'loningiz kanalda va qidiruvda ko'rinadi.", parse_mode="HTML", reply_markup=get_main_menu())
        await state.clear()
    elif message.text == "❌ Bekor qilish":
        await message.answer("🚫 <b>Bekor qilindi.</b>", parse_mode="HTML", reply_markup=get_main_menu())
        await state.clear()
    elif message.text == "⬅️ Orqaga":
        await state.set_state(SellPhone.contact)
        await message.answer("📞 Telefon raqamingizni yuboring:", reply_markup=get_contact_keyboard())
