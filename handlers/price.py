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
    get_replaced_parts_keyboard, get_defects_keyboard, get_screen_body_condition_keyboard,
    get_skip_keyboard,
    REPLACED_PARTS, DEFECTS_LIST
)
from database import add_price_request, get_user_language
from config import config
from strings import STRINGS

router = Router()

from phones.utils import calculate_phone_price

def calculate_price(data):
    return calculate_phone_price(data)

@router.message(F.text.in_(["💰 Narxlatish", "💰 Оценка"]))
async def start_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(PricePhone.choice)
    await message.answer(STRINGS[lang]['prompt_choice'], parse_mode="HTML", reply_markup=get_choice_keyboard(lang, 'price'))

@router.message(PricePhone.choice)
async def process_choice(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_continue_bot'] or message.text in ["➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(PricePhone.model)
        await message.answer(STRINGS[lang]['prompt_price_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))
    elif message.text == STRINGS[lang]['btn_back']:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    elif message.text.startswith("iPhone"):
        # User directly selected a model from a previous keyboard or typed it
        await state.update_data(model=message.text)
        await state.set_state(PricePhone.color)
        await message.answer(STRINGS[lang]['prompt_color'], parse_mode="HTML", reply_markup=get_color_keyboard(message.text, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_choice'], parse_mode="HTML", reply_markup=get_choice_keyboard(lang, 'price'))

@router.message(PricePhone.model)
async def process_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.choice)
        await message.answer(STRINGS[lang]['prompt_choice'], parse_mode="HTML", reply_markup=get_choice_keyboard(lang, 'price'))
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
    await state.set_state(PricePhone.memory)
    await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))

@router.message(PricePhone.memory)
async def process_memory(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        data = await state.get_data()
        await state.set_state(PricePhone.color)
        await message.answer(STRINGS[lang]['prompt_color'], parse_mode="HTML", reply_markup=get_color_keyboard(data.get('model'), lang))
        return
    
    await state.update_data(storage=message.text)
    await state.set_state(PricePhone.photos)
    await state.update_data(photos=[])
    await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))

@router.message(PricePhone.photos, F.photo)
async def process_photos_photo(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    photo_id = message.photo[-1].file_id
    await state.update_data(photos=[photo_id])
    
    # Automatically proceed after 1 photo
    await state.set_state(PricePhone.battery)
    await message.answer(STRINGS[lang]['prompt_price_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(PricePhone.photos, F.text)
async def process_photos_text(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.memory)
        await message.answer(STRINGS[lang]['prompt_price_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
        return
        
    if message.text in ["➡️ Davom etish", "➡️ Продолжить"]:
        data = await state.get_data()
        if not data.get('photos'):
            await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML")
            return
        await state.set_state(PricePhone.battery)
        await message.answer(STRINGS[lang]['prompt_price_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML")

@router.message(PricePhone.battery)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.photos)
        await message.answer(STRINGS[lang]['prompt_price_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))
        return

    if not message.text.isdigit() or not (1 <= int(message.text) <= 100):
        await message.answer(STRINGS[lang]['err_battery'], parse_mode="HTML")
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
    await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard([], lang))

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
    
    # Find which part was toggled
    toggled_key = None
    for key, string_key, icon in REPLACED_PARTS:
        label = STRINGS[lang][string_key]
        if message.text == f"{icon} {label}" or message.text == f"✅ {icon} {label}":
            toggled_key = key
            break
            
    if toggled_key:
        if toggled_key == "almashtirilmagan":
            selected = ["almashtirilmagan"]
        else:
            if "almashtirilmagan" in selected: selected.remove("almashtirilmagan")
            if toggled_key in selected: selected.remove(toggled_key)
            else: selected.append(toggled_key)
            
        await state.update_data(replaced_parts=selected)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard(selected, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard(selected, lang))

@router.message(PricePhone.defects)
async def process_defects_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        data = await state.get_data()
        await state.set_state(PricePhone.replaced_parts)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard(data.get('replaced_parts', []), lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(PricePhone.screen_condition)
        await message.answer(STRINGS[lang]['prompt_price_screen_condition'], parse_mode="HTML", reply_markup=get_screen_body_condition_keyboard(lang))
        return

    # Toggle logic
    data = await state.get_data()
    selected = data.get('defects', [])
    
    # Find which defect was toggled
    toggled_key = None
    for key, string_key, icon in DEFECTS_LIST:
        label = STRINGS[lang][string_key]
        if message.text == f"{icon} {label}" or message.text == f"✅ {icon} {label}":
            toggled_key = key
            break
            
    if toggled_key:
        if toggled_key == "hammasi_ishlaydi":
            selected = ["hammasi_ishlaydi"]
        else:
            if "hammasi_ishlaydi" in selected: selected.remove("hammasi_ishlaydi")
            if toggled_key in selected: selected.remove(toggled_key)
            else: selected.append(toggled_key)
            
        await state.update_data(defects=selected)
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard(selected, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard(selected, lang))

@router.message(PricePhone.screen_condition)
async def process_screen_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        data = await state.get_data()
        await state.set_state(PricePhone.defects)
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard(data.get('defects', []), lang))
        return
    
    await state.update_data(screen_condition=message.text)
    await state.set_state(PricePhone.body_condition)
    await message.answer(STRINGS[lang]['prompt_price_body_condition'], parse_mode="HTML", reply_markup=get_screen_body_condition_keyboard(lang))

@router.message(PricePhone.region)
async def process_region(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(PricePhone.body_condition)
        await message.answer(STRINGS[lang]['prompt_price_body_condition'], parse_mode="HTML", reply_markup=get_screen_body_condition_keyboard(lang))
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
    
    s = STRINGS[lang]
    parts_list = data.get('replaced_parts', [])
    defects_list = data.get('defects', [])
    
    parts_labels = [s[string_key] for key, string_key, icon in REPLACED_PARTS if key in parts_list]
    defects_labels = [s[string_key] for key, string_key, icon in DEFECTS_LIST if key in defects_list]
    
    parts_str = ", ".join(parts_labels)
    defects_str = ", ".join(defects_labels)

    summary = (
        f"{s['summary_title']}\n\n"
        f"📱 <b>{s['lbl_model']}:</b> {data.get('model')}\n"
        f"🎨 <b>{s['lbl_color']}:</b> {data.get('color')}\n"
        f"💾 <b>{s['lbl_memory']}:</b> {data.get('storage')}\n"
        f"🔋 <b>{s['lbl_battery']}:</b> {data.get('battery')}%\n"
        f"🔄 <b>{s['lbl_cycles']}:</b> {data.get('cycles')}\n"
        f"🔧 <b>{s['lbl_replaced']}:</b> {parts_str or s['val_none']}\n"
        f"⚠️ <b>{s['lbl_defects']}:</b> {defects_str or s['val_none']}\n"
        f"📱 <b>Ekran:</b> {data.get('screen_condition')}\n"
        f"📐 <b>Korpus:</b> {data.get('body_condition')}\n"
        f"🌍 <b>{s['lbl_region']}:</b> {data.get('region')}\n"
        f"📦 <b>{s['lbl_box']}:</b> {data.get('box')}\n"
        f"🛠 <b>{s['prompt_is_opened']}:</b> {data.get('is_opened')}"
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

