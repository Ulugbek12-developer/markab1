from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import SellPhone
from keyboards import (
    get_iphone_models_keyboard, get_memory_keyboard, get_condition_keyboard, 
    get_contact_keyboard, get_confirm_keyboard, get_back_keyboard, get_main_menu,
    get_admin_keyboard, get_region_keyboard, get_box_keyboard,
    get_choice_keyboard, get_color_keyboard, get_continue_keyboard,
    get_yes_no_keyboard, get_replaced_parts_keyboard, get_defects_keyboard,
    REPLACED_PARTS, DEFECTS_LIST
)
from database import add_ad, get_user_language
from config import config
from strings import STRINGS

router = Router()

@router.message(F.text.in_(["📱 Telefon sotish", "📱 Продать телефон"]))
async def start_sell(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(SellPhone.choice)
    await message.answer(STRINGS[lang]['prompt_choice'], parse_mode="HTML", reply_markup=get_choice_keyboard(lang, 'sell'))

@router.message(SellPhone.choice)
async def process_choice(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_continue_bot'] or "davom etish" in message.text.lower() or "продолжить" in message.text.lower():
        await state.set_state(SellPhone.model)
        await message.answer(STRINGS[lang]['prompt_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))
    elif message.text == STRINGS[lang]['btn_back']:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_choice'])

@router.message(SellPhone.model)
async def process_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.choice)
        await message.answer(STRINGS[lang]['prompt_choice'], reply_markup=get_choice_keyboard(lang, 'sell'))
        return
    
    await state.update_data(model=message.text)
    await state.set_state(SellPhone.color)
    await message.answer(STRINGS[lang]['prompt_color'], parse_mode="HTML", reply_markup=get_color_keyboard(message.text, lang))

@router.message(SellPhone.color)
async def process_color(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.model)
        await message.answer(STRINGS[lang]['prompt_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))
        return
    
    await state.update_data(color=message.text)
    await state.set_state(SellPhone.photos)
    await state.update_data(photos=[])
    await message.answer(STRINGS[lang]['prompt_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))

@router.message(SellPhone.photos, F.photo)
async def process_photos_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

@router.message(SellPhone.photos, F.text)
async def process_photos_text(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        data = await state.get_data()
        await state.set_state(SellPhone.color)
        await message.answer(STRINGS[lang]['prompt_color'], reply_markup=get_color_keyboard(data.get('model'), lang))
        return
        
    if message.text in ["➡️ Davom etish", "➡️ Продолжить"]:
        data = await state.get_data()
        if not data.get('photos'):
            await message.answer(STRINGS[lang]['prompt_photos'])
            return
        await state.set_state(SellPhone.battery)
        await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_photos'])

@router.message(SellPhone.battery)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.photos)
        await message.answer(STRINGS[lang]['prompt_photos'], reply_markup=get_continue_keyboard(lang))
        return

    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer(STRINGS[lang]['err_battery'])
        return

    await state.update_data(battery=message.text)
    await state.set_state(SellPhone.cycles)
    await message.answer(STRINGS[lang]['prompt_cycles'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(SellPhone.cycles)
async def process_cycles(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.battery)
        await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    if not message.text.isdigit():
        await message.answer("🔢 Iltimos, tsikl sonini raqamda kiriting:")
        return

    await state.update_data(cycles=message.text)
    await state.set_state(SellPhone.replaced_parts)
    await state.update_data(replaced_parts=[])
    await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard([]))

@router.message(SellPhone.replaced_parts)
async def process_replaced_parts_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        await state.set_state(SellPhone.cycles)
        await message.answer(STRINGS[lang]['prompt_cycles'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(SellPhone.defects)
        await state.update_data(defects=[])
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard([], lang))
        return

    # Toggle logic
    data = await state.get_data()
    selected = data.get('replaced_parts', [])
    text = message.text.replace("✅ ", "")
    
    # Find key by label
    part_key = None
    for key, label in REPLACED_PARTS:
        if label == text:
            part_key = key
            break
            
    if part_key:
        if part_key == "almashtirilmagan":
            selected = ["almashtirilmagan"]
        else:
            if "almashtirilmagan" in selected: selected.remove("almashtirilmagan")
            if part_key in selected: selected.remove(part_key)
            else: selected.append(part_key)
            
        await state.update_data(replaced_parts=selected)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], reply_markup=get_replaced_parts_keyboard(selected, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], reply_markup=get_replaced_parts_keyboard(selected, lang))

@router.message(SellPhone.defects)
async def process_defects_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        data = await state.get_data()
        await state.set_state(SellPhone.replaced_parts)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], reply_markup=get_replaced_parts_keyboard(data.get('replaced_parts', []), lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(SellPhone.memory)
        await message.answer(STRINGS[lang]['prompt_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
        return

    # Toggle logic
    data = await state.get_data()
    selected = data.get('defects', [])
    text = message.text.replace("✅ ", "")
    
    # Find key by label
    defect_key = None
    for key, label in DEFECTS_LIST:
        if label == text:
            defect_key = key
            break
            
    if defect_key:
        if defect_key == "hammasi_ishlaydi":
            selected = ["hammasi_ishlaydi"]
        else:
            if "hammasi_ishlaydi" in selected: selected.remove("hammasi_ishlaydi")
            if defect_key in selected: selected.remove(defect_key)
            else: selected.append(defect_key)
            
        await state.update_data(defects=selected)
        await message.answer(STRINGS[lang]['prompt_defects'], reply_markup=get_defects_keyboard(selected, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_defects'], reply_markup=get_defects_keyboard(selected, lang))

@router.message(SellPhone.memory)
async def process_memory(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.defects)
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard([]))
        return
    
    await state.update_data(memory=message.text, storage=message.text)
    await state.set_state(SellPhone.condition)
    await message.answer(STRINGS[lang]['prompt_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))

@router.message(SellPhone.condition)
async def process_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.memory)
        await message.answer(STRINGS[lang]['prompt_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
        return
    
    await state.update_data(condition=message.text)
    await state.set_state(SellPhone.region)
    await message.answer(STRINGS[lang]['prompt_region'], parse_mode="HTML", reply_markup=get_region_keyboard(lang))

@router.message(SellPhone.region)
async def process_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.condition)
        await message.answer(STRINGS[lang]['prompt_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))
        return
    
    if message.text in ["Boshqa", "Другое"]:
        await state.update_data(awaiting_manual_region=True)
        await message.answer("🌍 <b>Region nomini yozing:</b>", parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    await state.update_data(region=message.text)
    await state.set_state(SellPhone.box)
    await message.answer(STRINGS[lang]['prompt_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))

@router.message(SellPhone.box)
async def process_box(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.region)
        await message.answer(STRINGS[lang]['prompt_region'], reply_markup=get_region_keyboard(lang))
        return

    await state.update_data(box=message.text)
    await state.set_state(SellPhone.price)
    await message.answer(STRINGS[lang]['prompt_price'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(SellPhone.price)
async def process_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.box)
        await message.answer(STRINGS[lang]['prompt_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))
        return

    await state.update_data(price=message.text)
    await state.set_state(SellPhone.contact)
    await message.answer(STRINGS[lang]['prompt_contact'], parse_mode="HTML", reply_markup=get_contact_keyboard(lang))

@router.message(SellPhone.contact, F.contact | F.text)
async def process_contact(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.price)
        await message.answer(STRINGS[lang]['prompt_price'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    phone = message.contact.phone_number if message.contact else message.text
    username = message.from_user.username
    if username: phone = f"{phone} (@{username})"
    await state.update_data(contact=phone)
    
    data = await state.get_data()
    
    # Format replaced parts and defects for summary
    parts_list = data.get('replaced_parts', [])
    defects_list = data.get('defects', [])
    parts_str = ", ".join([label for key, label in REPLACED_PARTS if key in parts_list])
    defects_str = ", ".join([label for key, label in DEFECTS_LIST if key in defects_list])

    summary = (
        f"{STRINGS[lang]['summary_title']}\n\n"
        f"📱 <b>{STRINGS[lang]['lbl_model']}:</b> {data['model']}\n"
        f"🎨 <b>{STRINGS[lang]['lbl_color']}:</b> {data.get('color')}\n"
        f"💾 <b>{STRINGS[lang]['lbl_memory']}:</b> {data['memory']}\n"
        f"🔋 <b>{STRINGS[lang]['lbl_battery']}:</b> {data['battery']}%\n"
        f"🔄 <b>{STRINGS[lang]['lbl_cycles']}:</b> {data.get('cycles')}\n"
        f"🔧 <b>Almashtirilgan:</b> {parts_str or 'Yo''q'}\n"
        f"⚠️ <b>Nosozliklar:</b> {defects_str or 'Yo''q'}\n"
        f"✨ <b>{STRINGS[lang]['lbl_condition']}:</b> {data['condition']}\n"
        f"🌍 <b>{STRINGS[lang]['lbl_region']}:</b> {data['region']}\n"
        f"📦 <b>{STRINGS[lang]['lbl_box']}:</b> {data['box']}\n"
        f"💰 <b>{STRINGS[lang]['lbl_price']}:</b> {data['price']}\n"
        f"📞 <b>{STRINGS[lang]['lbl_contact']}:</b> {data['contact']}"
    )
    
    await state.set_state(SellPhone.confirm)
    await message.answer_photo(photo=data['photos'][0], caption=summary + "\n\n" + STRINGS[lang]['prompt_confirm'], parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))

@router.message(SellPhone.confirm)
async def process_confirm(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.contact)
        await message.answer(STRINGS[lang]['prompt_contact'], parse_mode="HTML", reply_markup=get_contact_keyboard(lang))
        return
        
    if message.text == STRINGS[lang]['btn_confirm']:
        data = await state.get_data()
        data['user_id'] = message.from_user.id
        data['storage'] = data['memory']
        ad_id = await add_ad(data)
        
        from handlers.price import calculate_price
        recommended_price = calculate_price(data)
        
        if config.ADMIN_ID:
            admin_text = f"🆕 <b>YANGI E'LON (ID: {ad_id})</b>\n\n"
            admin_text += f"👤 User: {message.from_user.full_name}\n"
            admin_text += f"📱 Model: {data['model']} ({data.get('color')})\n"
            admin_text += f"💰 Narxi: {data['price']}\n"
            admin_text += f"📐 Taxminiy: {recommended_price} mln so'm"
            await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_text, reply_markup=get_admin_keyboard(ad_id, lang), parse_mode="HTML")

        await message.answer(STRINGS[lang]['sell_success'].format(price=recommended_price), parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    else:
        await message.answer(STRINGS[lang]['msg_cancelled'], parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
