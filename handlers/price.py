from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import PricePhone
from keyboards import (
    get_iphone_models_keyboard, get_memory_keyboard,
    get_condition_keyboard, get_region_keyboard, get_box_keyboard,
    get_main_menu, get_back_keyboard, get_price_admin_keyboard,
    get_choice_keyboard, get_color_keyboard, get_opened_keyboard,
    get_confirm_keyboard, get_continue_keyboard, get_yes_no_keyboard,
    get_replaced_parts_keyboard, get_defects_keyboard,
    REPLACED_PARTS, DEFECTS_LIST
)
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
    "iPhone 17 Pro Max": 1600
}

def calculate_price(data):
    model = data.get('model', "")
    base = BASE_PRICES.get(model, 500)
    
    # Memory adjustments
    storage = str(data.get('storage', "128GB"))
    if "256" in storage: base += 50
    elif "512" in storage: base += 100
    elif "1TB" in storage: base += 200
    
    # Battery adjustments
    try:
        battery_val = int(data.get('battery', 90))
        if battery_val >= 90: pass
        elif battery_val >= 80: base -= 30
        elif battery_val >= 70: base -= 60
        else: base -= 100
    except: pass
    
    # Cycles
    try:
        cycles = int(data.get('cycles', 0))
        if cycles > 1000: base -= 50
        elif cycles > 500: base -= 30
    except: pass

    # Condition
    cond = str(data.get('condition', "")).lower()
    if "yaxshi" in cond or "хороший" in cond: base -= 50
    elif "yomon" in cond or "плохое" in cond: base -= 150
    
    # Box
    box = str(data.get('box', '')).lower()
    if "yo'q" in box or 'нет' in box: base -= 30
    
    # Replaced parts deductions
    replaced_parts = data.get('replaced_parts', [])
    if "almashtirilmagan" not in replaced_parts:
        for part in replaced_parts:
            if part == "ekran": base -= 100
            elif part == "batareya": base -= 30
            elif part == "kamera": base -= 70
            elif part == "orqa_qopqoq": base -= 40
            else: base -= 20
            
    # Defects deductions
    defects = data.get('defects', [])
    if "hammasi_ishlaydi" not in defects:
        for defect in defects:
            if defect == "face_id": base -= 150
            elif defect == "true_tone": base -= 50
            elif defect == "asosiy_kamera": base -= 100
            elif defect == "old_kamera": base -= 60
            elif defect == "wifi_bt": base -= 80
            else: base -= 30

    return round(base / 100, 1)

@router.message(F.text.in_(["💰 Narxlatish", "💰 Оценка"]))
async def start_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(PricePhone.choice)
    await message.answer(STRINGS[lang]['prompt_choice'], parse_mode="HTML", reply_markup=get_choice_keyboard(lang, 'price'))

@router.message(PricePhone.choice)
async def process_choice(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_continue_bot'] or "davom etish" in message.text.lower() or "продолжить" in message.text.lower():
        await state.set_state(PricePhone.model)
        await message.answer(STRINGS[lang]['prompt_price_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))
    elif message.text == STRINGS[lang]['btn_back']:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_choice'])

@router.message(PricePhone.model)
async def process_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.choice)
        await message.answer(STRINGS[lang]['prompt_choice'], reply_markup=get_choice_keyboard(lang, 'price'))
        return
    
    await state.update_data(model=message.text)
    await state.set_state(PricePhone.color)
    await message.answer(STRINGS[lang]['prompt_color'], parse_mode="HTML", reply_markup=get_color_keyboard(message.text, lang))

@router.message(PricePhone.color)
async def process_color(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.model)
        await message.answer(STRINGS[lang]['prompt_price_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))
        return
    
    await state.update_data(color=message.text)
    await state.set_state(PricePhone.photos)
    await state.update_data(photos=[])
    await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))

@router.message(PricePhone.photos, F.photo)
async def process_photos_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

@router.message(PricePhone.photos, F.text)
async def process_photos_text(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        data = await state.get_data()
        await state.set_state(PricePhone.color)
        await message.answer(STRINGS[lang]['prompt_color'], reply_markup=get_color_keyboard(data.get('model'), lang))
        return
        
    if message.text in ["➡️ Davom etish", "➡️ Продолжить"]:
        data = await state.get_data()
        if not data.get('photos'):
            await message.answer(STRINGS[lang]['prompt_price_photos'])
            return
        await state.set_state(PricePhone.battery)
        await message.answer(STRINGS[lang]['prompt_price_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_price_photos'])

@router.message(PricePhone.battery)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.photos)
        await message.answer(STRINGS[lang]['prompt_price_photos'], reply_markup=get_continue_keyboard(lang))
        return

    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer(STRINGS[lang]['err_battery'])
        return

    await state.update_data(battery=message.text)
    await state.set_state(PricePhone.cycles)
    await message.answer(STRINGS[lang]['prompt_cycles'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(PricePhone.cycles)
async def process_cycles(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.battery)
        await message.answer(STRINGS[lang]['prompt_price_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    if not message.text.isdigit():
        await message.answer("🔢 Iltimos, tsikl sonini raqamda kiriting:")
        return

    await state.update_data(cycles=message.text)
    await state.set_state(PricePhone.replaced_parts)
    await state.update_data(replaced_parts=[])
    await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard([]))

@router.message(PricePhone.replaced_parts)
async def process_replaced_parts_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        await state.set_state(PricePhone.cycles)
        await message.answer(STRINGS[lang]['prompt_cycles'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(PricePhone.defects)
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

@router.message(PricePhone.defects)
async def process_defects_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        data = await state.get_data()
        await state.set_state(PricePhone.replaced_parts)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], reply_markup=get_replaced_parts_keyboard(data.get('replaced_parts', []), lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(PricePhone.memory)
        await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
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

@router.message(PricePhone.memory)
async def process_memory(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.defects)
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard([]))
        return
    
    await state.update_data(storage=message.text)
    await state.set_state(PricePhone.condition)
    await message.answer(STRINGS[lang]['prompt_price_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))

@router.message(PricePhone.condition)
async def process_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.memory)
        await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
        return
    
    await state.update_data(condition=message.text)
    await state.set_state(PricePhone.region)
    await message.answer(STRINGS[lang]['prompt_price_region'], parse_mode="HTML", reply_markup=get_region_keyboard(lang))

@router.message(PricePhone.region)
async def process_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.condition)
        await message.answer(STRINGS[lang]['prompt_price_condition'], parse_mode="HTML", reply_markup=get_condition_keyboard(lang))
        return
    
    if message.text in ["Boshqa", "Другое"]:
        await state.set_state(PricePhone.manual_region)
        await message.answer(STRINGS[lang]['prompt_manual_region'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return
        
    await state.update_data(region=message.text)
    await state.set_state(PricePhone.box)
    await message.answer(STRINGS[lang]['prompt_price_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))

@router.message(PricePhone.manual_region)
async def process_manual_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.region)
        await message.answer(STRINGS[lang]['prompt_price_region'], reply_markup=get_region_keyboard(lang))
        return
    await state.update_data(region=message.text)
    await state.set_state(PricePhone.box)
    await message.answer(STRINGS[lang]['prompt_price_box'], parse_mode="HTML", reply_markup=get_box_keyboard(lang))

@router.message(PricePhone.box)
async def process_box(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.region)
        await message.answer(STRINGS[lang]['prompt_price_region'], reply_markup=get_region_keyboard(lang))
        return
    
    await state.update_data(box=message.text)
    await state.set_state(PricePhone.is_opened)
    await message.answer(STRINGS[lang]['prompt_is_opened'], parse_mode="HTML", reply_markup=get_opened_keyboard(lang))

@router.message(PricePhone.is_opened)
async def process_is_opened(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.box)
        await message.answer(STRINGS[lang]['prompt_price_box'], reply_markup=get_box_keyboard(lang))
        return
        
    await state.update_data(is_opened=message.text)
    data = await state.get_data()
    
    # Format replaced parts and defects for summary
    parts_list = data.get('replaced_parts', [])
    defects_list = data.get('defects', [])
    parts_str = ", ".join([label for key, label in REPLACED_PARTS if key in parts_list])
    defects_str = ", ".join([label for key, label in DEFECTS_LIST if key in defects_list])

    summary = (
        f"{STRINGS[lang]['summary_title']}\n\n"
        f"📱 <b>{STRINGS[lang]['lbl_model']}:</b> {data.get('model')}\n"
        f"🎨 <b>{STRINGS[lang]['lbl_color']}:</b> {data.get('color')}\n"
        f"💾 <b>{STRINGS[lang]['lbl_memory']}:</b> {data.get('storage')}\n"
        f"🔋 <b>{STRINGS[lang]['lbl_battery']}:</b> {data.get('battery')}%\n"
        f"🔄 <b>{STRINGS[lang]['lbl_cycles']}:</b> {data.get('cycles')}\n"
        f"🔧 <b>Almashtirilgan:</b> {parts_str or 'Yo''q'}\n"
        f"⚠️ <b>Nosozliklar:</b> {defects_str or 'Yo''q'}\n"
        f"✨ <b>{STRINGS[lang]['lbl_condition']}:</b> {data.get('condition')}\n"
        f"🌍 <b>{STRINGS[lang]['lbl_region']}:</b> {data.get('region')}\n"
        f"📦 <b>{STRINGS[lang]['lbl_box']}:</b> {data.get('box')}\n"
        f"🔧 <b>Ochilganmi:</b> {data.get('is_opened')}"
    )
    
    await state.set_state(PricePhone.confirm)
    await message.answer(summary + "\n\n" + STRINGS[lang]['prompt_confirm'], parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))

@router.message(PricePhone.confirm)
async def process_confirm(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.is_opened)
        await message.answer(STRINGS[lang]['prompt_is_opened'], reply_markup=get_opened_keyboard(lang))
        return
        
    if message.text == STRINGS[lang]['btn_confirm']:
        data = await state.get_data()
        recommended_price = calculate_price(data)
        
        # Save to DB
        data['user_id'] = message.from_user.id
        data['calculated_price'] = str(recommended_price)
        req_id = await add_price_request(data)
        
        # Admin Notification
        if config.ADMIN_ID:
            admin_text = f"🆕 <b>YANGI NARXLASH SO'ROVI (ID: {req_id})</b>\n\n"
            admin_text += f"👤 Mijoz: <a href='tg://user?id={message.from_user.id}'>{message.from_user.full_name}</a>\n"
            admin_text += f"📱 Model: {data.get('model')} ({data.get('color')})\n"
            admin_text += f"📐 Taxminiy: {recommended_price} mln so'm"
            await message.bot.send_photo(config.ADMIN_ID, data['photos'][0], caption=admin_text, parse_mode="HTML", reply_markup=get_price_admin_keyboard(req_id, lang))

        await message.answer(STRINGS[lang]['price_success'].format(price=recommended_price), parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    else:
        await message.answer(STRINGS[lang]['msg_cancelled'], reply_markup=get_main_menu(lang))
        await state.clear()

