from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import SellPhone
from keyboards import (
    get_iphone_models_keyboard, get_memory_keyboard, get_condition_keyboard, 
    get_contact_keyboard, get_confirm_keyboard, get_back_keyboard, get_main_menu,
    get_admin_keyboard, get_region_keyboard, get_box_keyboard
)
from database import add_ad, get_user_language
from config import config
from strings import STRINGS

router = Router()

@router.message(F.text.in_(["📱 Telefon sotish", "📱 Продать телефон"]))
async def start_sell(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(SellPhone.model)
    await message.answer(STRINGS[lang]['prompt_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))

@router.message(SellPhone.model)
async def process_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
        return
    
    await state.update_data(model=message.text)
    await state.set_state(SellPhone.photos)
    await state.update_data(photos=[])
    await message.answer(STRINGS[lang]['prompt_photos'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(SellPhone.photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    
    await state.set_state(SellPhone.battery)
    await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(SellPhone.battery)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.model)
        await message.answer(STRINGS[lang]['prompt_model'], reply_markup=get_iphone_models_keyboard(lang))
        return

    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer(STRINGS[lang]['err_battery'])
        return

    await state.update_data(battery=message.text)
    await state.set_state(SellPhone.memory)
    await message.answer(STRINGS[lang]['prompt_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))

@router.message(SellPhone.memory)
async def process_memory(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.battery)
        await message.answer(STRINGS[lang]['prompt_battery'], reply_markup=get_back_keyboard(lang))
        return

    await state.update_data(memory=message.text, storage=message.text)
    await state.set_state(SellPhone.condition)
    await message.answer(STRINGS[lang]['prompt_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))

@router.message(SellPhone.condition)
async def process_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.memory)
        await message.answer(STRINGS[lang]['prompt_memory'], reply_markup=get_memory_keyboard(lang))
        return

    await state.update_data(condition=message.text)
    await state.set_state(SellPhone.region)
    await message.answer(STRINGS[lang]['prompt_region'], parse_mode="HTML", reply_markup=get_region_keyboard(lang))

@router.message(SellPhone.region)
async def process_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.condition)
        await message.answer(STRINGS[lang]['prompt_condition'], reply_markup=get_condition_keyboard(lang))
        return

    await state.update_data(region=message.text)
    await state.set_state(SellPhone.box)
    await message.answer(STRINGS[lang]['prompt_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))

@router.message(SellPhone.box)
async def process_box(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.region)
        await message.answer(STRINGS[lang]['prompt_region'], reply_markup=get_region_keyboard(lang))
        return

    await state.update_data(box=message.text)
    await state.set_state(SellPhone.price)
    await message.answer(STRINGS[lang]['prompt_price'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(SellPhone.price)
async def process_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(SellPhone.box)
        await message.answer(STRINGS[lang]['prompt_box'], reply_markup=get_box_keyboard(lang))
        return

    await state.update_data(price=message.text)
    await state.set_state(SellPhone.contact)
    await message.answer(STRINGS[lang]['prompt_contact'], parse_mode="HTML", reply_markup=get_contact_keyboard(lang))

@router.message(SellPhone.contact, F.contact | F.text)
async def process_contact(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Наzad"]:
        await state.set_state(SellPhone.price)
        await message.answer(STRINGS[lang]['prompt_price'], reply_markup=get_back_keyboard(lang))
        return

    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(contact=phone)
    
    data = await state.get_data()
    s = STRINGS[lang]
    summary = (
        f"{s['summary_title']}\n\n"
        f"📱 <b>{s['lbl_model']}:</b> {data['model']}\n"
        f"💾 <b>{s['lbl_memory']}:</b> {data['memory']}\n"
        f"🔋 <b>{s['lbl_battery']}:</b> {data['battery']}%\n"
        f"🛠 <b>{s['lbl_condition']}:</b> {data['condition']}\n"
        f"🌍 <b>{s['lbl_region']}:</b> {data['region']}\n"
        f"📦 <b>{s['lbl_box']}:</b> {data['box']}\n"
        f"💰 <b>{s['lbl_price']}:</b> {data['price']}\n"
        f"📞 <b>{s['lbl_contact']}:</b> {data['contact']}\n\n"
        f"{s['prompt_confirm']}"
    )
    
    await state.set_state(SellPhone.confirm)
    await message.answer_photo(photo=data['photos'][0], caption=summary, parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))

@router.message(SellPhone.confirm)
async def process_confirm(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text == s['btn_confirm']:
        data = await state.get_data()
        data['user_id'] = message.from_user.id
        data['storage'] = data['memory']
        ad_id = await add_ad(data)
        
        if config.ADMIN_ID != 0:
            admin_summary = f"🆕 <b>YANGI E'LON (ID: {ad_id})</b>\n\nUser: {message.from_user.full_name}\n" + \
                            f"Model: {data['model']}\nHotira: {data['memory']}\nYomkost: {data['battery']}%\n" + \
                            f"Narxi: {data['price']}\nAloqa: {data['contact']}"
            await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_summary, reply_markup=get_admin_keyboard(ad_id, lang), parse_mode="HTML")

        await message.answer(s['sell_success'], parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    elif message.text == s['btn_cancel']:
        await message.answer(s['msg_cancelled'], parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    elif message.text == s['btn_back']:
        await state.set_state(SellPhone.contact)
        await message.answer(s['prompt_contact'], reply_markup=get_contact_keyboard(lang))
