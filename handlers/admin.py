from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import AdminState, AdminAuth, AdminAddProduct, AdminBranchMgmt, AdminDeleteProduct
import keyboards
from database import update_ad_status, get_ad_by_id, update_price_request, get_price_request, add_ad, add_branch, get_all_branches, delete_branch, delete_ad, get_user_language
from config import config
from strings import STRINGS

router = Router()

ADMIN_PASSWORD = "MARKAB777" 

@router.message(F.text.in_(["🔐 Admin Panel", "🔐 Админ-панель"]))
async def admin_login(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAuth.waiting_for_password)
    await message.answer(STRINGS[lang]['prompt_admin_pass'], parse_mode="HTML", reply_markup=keyboards.get_main_menu(lang))

@router.message(AdminAuth.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text == ADMIN_PASSWORD:
        await state.clear()
        web_admin_url = "https://markab2.pythonanywhere.com/markab-admin/"
        text = STRINGS[lang]['admin_welcome'] + f"\n\n🌐 <b>Veb Admin Panel:</b>\n{web_admin_url}"
        await message.answer(text, parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard(lang))
    else:
        await message.answer(STRINGS[lang]['err_pass'], parse_mode="HTML")

@router.message(F.text.in_(["➕ Mahsulot qo'shish", "➕ Добавить товар"]))
async def admin_add_product_start(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminAddProduct.model)
    await message.answer(STRINGS[lang]['prompt_admin_model'], parse_mode="HTML", reply_markup=keyboards.get_iphone_models_keyboard(lang))

@router.message(AdminAddProduct.model)
async def admin_add_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=keyboards.get_admin_panel_keyboard(lang))
        await state.clear()
        return
    await state.update_data(model=message.text)
    await state.set_state(AdminAddProduct.branch)
    branches = await get_all_branches()
    await message.answer(STRINGS[lang]['prompt_admin_branch'], parse_mode="HTML", reply_markup=keyboards.get_branches_keyboard(branches, lang))

@router.message(AdminAddProduct.branch)
async def admin_add_branch(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(branch=message.text)
    await state.set_state(AdminAddProduct.storage)
    await message.answer(STRINGS[lang]['prompt_admin_storage'], parse_mode="HTML", reply_markup=keyboards.get_memory_keyboard(lang))

@router.message(AdminAddProduct.storage)
async def admin_add_storage(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(storage=message.text)
    await state.set_state(AdminAddProduct.battery)
    await message.answer(STRINGS[lang]['prompt_admin_battery'], parse_mode="HTML")

@router.message(AdminAddProduct.battery)
async def admin_add_battery(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(battery=message.text)
    await state.set_state(AdminAddProduct.condition)
    await message.answer(STRINGS[lang]['prompt_admin_condition'], parse_mode="HTML", reply_markup=keyboards.get_condition_keyboard(lang))

@router.message(AdminAddProduct.condition)
async def admin_add_condition(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(condition=message.text)
    await state.set_state(AdminAddProduct.price)
    await message.answer(STRINGS[lang]['prompt_admin_price'], parse_mode="HTML")

@router.message(AdminAddProduct.price)
async def admin_add_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.update_data(price=message.text)
    await state.set_state(AdminAddProduct.photos)
    await state.update_data(photos=[])
    from keyboards import get_continue_keyboard
    await message.answer(STRINGS[lang]['prompt_admin_photos'], parse_mode="HTML", reply_markup=get_continue_keyboard(lang))

@router.message(AdminAddProduct.photos, F.photo)
async def admin_add_photos_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get('photos', [])
    if len(photos) < 3:
        photos.append(message.photo[-1].file_id)
        await state.update_data(photos=photos)

@router.message(AdminAddProduct.photos, F.text)
async def admin_add_photos_text(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(AdminAddProduct.price)
        await message.answer(STRINGS[lang]['prompt_admin_price'], parse_mode="HTML")
        return
        
    if message.text in ["➡️ Davom etish", "➡️ Продолжить"]:
        data = await state.get_data()
        if not data.get('photos'):
            await message.answer(STRINGS[lang]['prompt_admin_photos'])
            return
            
        data['status'] = 'approved' # Direct approve
        data['user_id'] = message.from_user.id
        
        await add_ad(data)
    
    # Sync to Django (Web App)
    try:
        from phones.models import Phone
        from asgiref.sync import sync_to_async
        import os
        from core.settings import MEDIA_ROOT
        
        log_msg = f"DEBUG: Syncing {data.get('model')} to Web App...\n"
        with open('sync_debug.log', 'a') as f: f.write(log_msg)
        
        # Convert battery to int safely
        battery_str = str(data.get('battery', '100')).replace('%', '').strip()
        battery_val = int(battery_str) if battery_str.isdigit() else 100
        
        # Robust Price Parsing
        price_str = str(data.get('price', 0)).lower().replace(' ', '').replace(',', '').replace('so\'m', '').replace('som', '')
        if 'mln' in price_str:
            try: price_val = int(float(price_str.replace('mln', '').strip()) * 1000000)
            except: price_val = 0
        elif 'k' in price_str:
            try: price_val = int(float(price_str.replace('k', '').strip()) * 1000)
            except: price_val = 0
        else:
            import re
            nums = re.findall(r'\d+', price_str)
            price_val = int(''.join(nums)) if nums else 0

        # Map model and memory to match Django choices
        model_name = data.get('model', '')
        if model_name.startswith('iPhone '):
            model_name = model_name.replace('iPhone ', '')
        memory = str(data.get('storage', ''))
        if ' GB' in memory:
            memory = memory.replace(' GB', '')
            
        # Download photo
        image_rel_path = None
        if data.get('photos'):
            photo_id = data['photos'][0]
            file = await message.bot.get_file(photo_id)
            local_filename = f"{photo_id}.jpg"
            local_full_path = os.path.join(MEDIA_ROOT, 'phones', local_filename)
            os.makedirs(os.path.dirname(local_full_path), exist_ok=True)
            await message.bot.download_file(file.file_path, local_full_path)
            image_rel_path = f"phones/{local_filename}"

        # Map condition to Django choices
        bot_cond = str(data.get('condition', '')).lower()
        if 'ideal' in bot_cond or 'yangi' in bot_cond: django_cond = 'ideal'
        elif 'yaxshi' in bot_cond or 'medium' in bot_cond: django_cond = 'medium'
        else: django_cond = 'bad'

        phone_obj = await sync_to_async(Phone.objects.create)(
            model_name=model_name,
            memory=memory,
            battery_health=battery_val,
            color='Noma\'lum',
            price=price_val,
            condition=django_cond,
            is_approved=True,
            seller_phone=str(data.get('contact', '')),
            image=image_rel_path
        )
        with open('sync_debug.log', 'a') as f: f.write(f"DEBUG: SUCCESS! Product created in Django with ID: {phone_obj.id}\n")
        with open('sync_debug.log', 'a') as f: f.write(f"DEBUG: Sync Bot -> Web App success! ID: {phone_obj.id}\n")
    except Exception as e:
        import traceback
        err_msg = f"DEBUG: Sync Bot -> Web App error: {e}\n{traceback.format_exc()}\n"
        with open('sync_debug.log', 'a') as f: f.write(err_msg)

    await message.answer(STRINGS[lang]['admin_add_success'], parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard(lang))
    await state.clear()

@router.message(F.text.in_(["⬅️ Chiqish", "⬅️ Выход"]))
async def admin_exit(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.clear()
    await message.answer(STRINGS[lang]['msg_cancelled'], reply_markup=keyboards.get_main_menu(lang))

@router.message(F.text.in_(["🏢 Filiallarni boshqarish", "🏢 Управление филиалами"]))
async def admin_branch_mgmt(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await message.answer(STRINGS[lang]['admin_branch_menu'], parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard(lang))

@router.message(F.text.in_(["➕ Yangi filial qo'shish", "➕ Добавить филиал"]))
async def admin_add_branch_start(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminBranchMgmt.waiting_for_name)
    await message.answer(STRINGS[lang]['prompt_branch_name'], parse_mode="HTML")

@router.message(AdminBranchMgmt.waiting_for_name)
async def admin_add_branch_process(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await add_branch(message.text)
    await message.answer(STRINGS[lang]['branch_added'].format(name=message.text), parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard(lang))
    await state.clear()

@router.message(F.text.in_(["❌ Filialni o'chirish", "❌ Удалить филиал"]))
async def admin_delete_branch_start(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    branches = await get_all_branches()
    await state.set_state(AdminBranchMgmt.waiting_for_delete)
    await message.answer(STRINGS[lang]['prompt_delete_branch'], parse_mode="HTML", reply_markup=keyboards.get_branches_keyboard(branches, lang))

@router.message(AdminBranchMgmt.waiting_for_delete)
async def admin_delete_branch_process(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await admin_branch_mgmt(message, state)
        return
    await delete_branch(message.text)
    await message.answer(STRINGS[lang]['branch_deleted'].format(name=message.text), parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard(lang))
    await state.clear()

@router.message(F.text.in_(["⬅️ Admin menyuga qaytish", "⬅️ Вернуться в админ-меню"]))
async def admin_return(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await message.answer("🏠 Admin panel", reply_markup=keyboards.get_admin_panel_keyboard(lang))

@router.message(F.text.in_(["🗑 Mahsulotni o'chirish", "🗑 Удалить товар"]))
async def admin_delete_product_start(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(AdminDeleteProduct.waiting_for_model)
    await message.answer(STRINGS[lang]['prompt_delete_model'], parse_mode="HTML")

@router.message(AdminDeleteProduct.waiting_for_model)
async def admin_delete_product_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    model = message.text
    import sqlite3
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, model, storage, price FROM ads WHERE model LIKE ?", (f"%{model}%",))
    ads = cursor.fetchall()
    conn.close()
    
    if not ads:
        await message.answer(STRINGS[lang]['no_model_found'], parse_mode="HTML")
        return
    
    text = STRINGS[lang]['found_models']
    for ad in ads:
        text += f"🆔 {ad[0]} | {ad[1]} {ad[2]}GB | {ad[3]:,.0f} so'm\n"
    
    text += STRINGS[lang]['prompt_delete_id']
    await state.set_state(AdminDeleteProduct.waiting_for_selection)
    await message.answer(text, parse_mode="HTML")

@router.message(AdminDeleteProduct.waiting_for_selection)
async def admin_delete_product_finish(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    try:
        ad_id = int(message.text)
        await delete_ad(ad_id)
        await message.answer(STRINGS[lang]['ad_deleted'].format(id=ad_id), parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard(lang))
        await state.clear()
    except ValueError:
        await message.answer("❌ ID?")

@router.callback_query(F.data.startswith("approve_"))
async def approve_ad(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(callback.from_user.id)
    ad_id = int(callback.data.split("_")[1])
    
    branch = "malika"
    await update_ad_status(ad_id, "approved", branch=branch)
    ad = await get_ad_by_id(ad_id)
    
    # Save to Django DB
    try:
        from asgiref.sync import sync_to_async
        from phones.models import Phone
        await sync_to_async(Phone.objects.create)(
            model_name=ad['model'],
            memory=ad['storage'],
            battery_health=int(ad['battery']),
            condition=ad['condition'],
            price=int(ad['price']),
            seller_phone=ad['contact'],
            branch=branch,
            is_approved=True
        )
    except Exception as e:
        print(f"Error saving to Django DB: {e}")
    
    user_lang = await get_user_language(ad['user_id'])
    await callback.message.bot.send_message(ad['user_id'], STRINGS[user_lang]['ad_approved_user'].format(id=ad_id, branch=branch), parse_mode="HTML")
    await callback.message.edit_text(STRINGS[lang]['ad_approved_admin'].format(id=ad_id, branch=branch))
    await callback.answer()

@router.callback_query(F.data.startswith("reject_"))
async def reject_ad(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    ad_id = int(callback.data.split("_")[1])
    await update_ad_status(ad_id, "rejected")
    ad = await get_ad_by_id(ad_id)
    
    user_lang = await get_user_language(ad['user_id'])
    await callback.message.bot.send_message(ad['user_id'], STRINGS[user_lang]['ad_rejected_user'].format(id=ad_id), parse_mode="HTML")
    await callback.message.edit_text(STRINGS[lang]['ad_rejected_admin'].format(id=ad_id))
    await callback.answer()

@router.callback_query(F.data.startswith("setprice_"))
async def admin_set_price(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(callback.from_user.id)
    req_id = int(callback.data.split("_")[1])
    await state.update_data(req_id=req_id)
    await state.set_state(AdminState.setting_price)
    await callback.message.answer(STRINGS[lang]['prompt_set_price'], parse_mode="HTML")
    await callback.answer()

@router.message(AdminState.setting_price)
async def process_admin_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.from_user.id != config.ADMIN_ID: return
    
    data = await state.get_data()
    req_id = data['req_id']
    price = message.text
    
    await update_price_request(req_id, price)
    req = await get_price_request(req_id)
    
    user_lang = await get_user_language(req['user_id'])
    await message.bot.send_message(req['user_id'], STRINGS[user_lang]['price_sent_user'].format(model=req['model'], price=price), parse_mode="HTML")
    await message.answer(STRINGS[lang]['price_sent_admin'], reply_markup=keyboards.get_admin_panel_keyboard(lang))
    await state.clear()

@router.callback_query(F.data.startswith("counter_"))
async def counter_offer_start(callback: CallbackQuery, state: FSMContext):
    lang = await get_user_language(callback.from_user.id)
    ad_id = int(callback.data.split("_")[1])
    await state.update_data(ad_id=ad_id)
    await state.set_state(AdminState.counter_price)
    await callback.message.answer(STRINGS[lang]['prompt_counter_price'], parse_mode="HTML")
    await callback.answer()

@router.message(AdminState.counter_price)
async def process_counter_price(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.from_user.id != config.ADMIN_ID: return
    
    data = await state.get_data()
    ad_id = data['ad_id']
    price = message.text
    
    ad = await get_ad_by_id(ad_id)
    if ad:
        user_lang = await get_user_language(ad['user_id'])
        await message.bot.send_message(
            ad['user_id'], 
            STRINGS[user_lang]['counter_sent_user'].format(price=price), 
            parse_mode="HTML",
            reply_markup=keyboards.get_user_counter_response_keyboard(ad_id)
        )
        await message.answer(STRINGS[lang]['counter_sent_admin'], reply_markup=keyboards.get_admin_panel_keyboard(lang))
    
    await state.clear()

@router.callback_query(F.data.startswith("user_agree_"))
async def handle_user_agree(callback: CallbackQuery):
    ad_id = int(callback.data.split("_")[2])
    
    # Send success message to user
    await callback.message.edit_text(
        "✅ <b>Tabriklaymiz!</b>\n\nSizning telefoningiz telegram kanalga joylanadi va siz bilan adminlarimiz aloqaga chiqadi. 🎉", 
        parse_mode="HTML"
    )
    
    # Notify Admin
    ad = await get_ad_by_id(ad_id)
    if ad:
        await callback.bot.send_message(
            config.ADMIN_ID, 
            f"🎉 <b>Mijoz rozi bo'ldi!</b> (E'lon ID: {ad_id})\n\n📞 Aloqa: {ad.get('contact', 'Noma\'lum')}",
            parse_mode="HTML"
        )
    await callback.answer()

@router.callback_query(F.data.startswith("user_disagree_"))
async def handle_user_disagree(callback: CallbackQuery):
    await callback.message.edit_text(
        "❌ <b>Afsus...</b>\n\nIltimos, narxni admin bilan kelishing:\n👨‍💻 Admin: @markab_admin", 
        parse_mode="HTML"
    )
    await callback.answer()
