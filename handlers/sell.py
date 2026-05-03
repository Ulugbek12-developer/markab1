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
    lang = await get_user_language(message.from_user.id)
    photo_id = message.photo[-1].file_id
    await state.update_data(photos=[photo_id])
    
    # Automatically proceed after 1 photo
    await state.set_state(SellPhone.battery)
    await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

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
            await message.answer(STRINGS[lang]['prompt_photos'], parse_mode="HTML")
            return
        await state.set_state(SellPhone.battery)
        await message.answer(STRINGS[lang]['prompt_battery'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
    else:
        await message.answer(STRINGS[lang]['prompt_photos'], parse_mode="HTML")

@router.message(SellPhone.battery)
async def process_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == STRINGS[lang]['btn_back']:
        await state.set_state(SellPhone.photos)
        await message.answer(STRINGS[lang]['prompt_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))
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
        await message.answer(STRINGS[lang]['prompt_battery'], reply_markup=get_back_keyboard(lang))
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

@router.message(SellPhone.defects)
async def process_defects_message(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    
    if message.text == s['btn_back']:
        data = await state.get_data()
        await state.set_state(SellPhone.replaced_parts)
        await message.answer(STRINGS[lang]['prompt_replaced_parts'], parse_mode="HTML", reply_markup=get_replaced_parts_keyboard(data.get('replaced_parts', []), lang))
        return
        
    if message.text in [s['btn_continue'], "➡️ Davom etish", "➡️ Продолжить"]:
        await state.set_state(SellPhone.memory)
        await message.answer(STRINGS[lang]['prompt_memory'], parse_mode="HTML", reply_markup=get_memory_keyboard(lang))
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
            if defect_key in selected: selected.remove(defect_key)
            else: selected.append(defect_key)
            
        await state.update_data(defects=selected)
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard(selected, lang))
    else:
        await message.answer(STRINGS[lang]['prompt_defects'], parse_mode="HTML", reply_markup=get_defects_keyboard(selected, lang))

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
    s = STRINGS[lang]
    parts_list = data.get('replaced_parts', [])
    defects_list = data.get('defects', [])
    
    parts_labels = [s[string_key] for _, string_key, _ in REPLACED_PARTS if _ in parts_list]
    defects_labels = [s[string_key] for _, string_key, _ in DEFECTS_LIST if _ in defects_list]
    
    parts_str = ", ".join(parts_labels)
    defects_str = ", ".join(defects_labels)

    summary = (
        f"{s['summary_title']}\n\n"
        f"📱 <b>{s['lbl_model']}:</b> {data['model']}\n"
        f"🎨 <b>{s['lbl_color']}:</b> {data.get('color')}\n"
        f"💾 <b>{s['lbl_memory']}:</b> {data['memory']}\n"
        f"🔋 <b>{s['lbl_battery']}:</b> {data['battery']}%\n"
        f"🔄 <b>{s['lbl_cycles']}:</b> {data.get('cycles')}\n"
        f"🔧 <b>{s['lbl_replaced']}:</b> {parts_str or s['val_none']}\n"
        f"⚠️ <b>{s['lbl_defects']}:</b> {defects_str or s['val_none']}\n"
        f"✨ <b>{s['lbl_condition']}:</b> {data['condition']}\n"
        f"🌍 <b>{s['lbl_region']}:</b> {data['region']}\n"
        f"📦 <b>{s['lbl_box']}:</b> {data['box']}\n"
        f"💰 <b>{s['lbl_price']}:</b> {data['price']}\n"
        f"📞 <b>{s['lbl_contact']}:</b> {data['contact']}"
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
        
        # --- SYNC TO DJANGO WEB APP ---
        try:
            from asgiref.sync import sync_to_async
            import os
            from core.settings import MEDIA_ROOT
            from phones.models import Listing, Category

            # Photo Download
            image_rel_path = None
            if data.get('photos'):
                photo_id = data['photos'][0]
                file = await message.bot.get_file(photo_id)
                local_filename = f"{photo_id}.jpg"
                local_full_path = os.path.join(MEDIA_ROOT, 'listings', local_filename)
                os.makedirs(os.path.dirname(local_full_path), exist_ok=True)
                await message.bot.download_file(file.file_path, local_full_path)
                image_rel_path = f"listings/{local_filename}"

            # Data Mapping
            apple_cat = await sync_to_async(Category.objects.filter(name__icontains='iPhone').first)()
            
            # Create Django record (initially not approved for users)
            await sync_to_async(Listing.objects.create)(
                title=f"iPhone {data['model']} {data['memory']}",
                model_name=data['model'],
                memory=data['memory'].replace(' GB', ''),
                battery_health=int(str(data.get('battery', 100)).replace('%', '').strip()),
                price=recommended_price * 1000000, # Approximate
                is_approved=False, # Wait for admin
                seller_phone=str(data.get('contact', '')),
                image=image_rel_path,
                category=apple_cat
            )
        except Exception as e:
            with open('sync_debug.log', 'a') as f: f.write(f"ERROR: Sync in sell.py: {e}\n")
        # -----------------------------
        
        await state.clear()
    else:
        await message.answer(STRINGS[lang]['msg_cancelled'], parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
