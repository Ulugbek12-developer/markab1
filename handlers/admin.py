from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import AdminState, AdminAuth, AdminAddProduct, AdminBranchMgmt, AdminDeleteProduct
import keyboards
from database import update_ad_status, get_ad_by_id, update_price_request, get_price_request, add_ad, add_branch, get_all_branches, delete_branch, delete_ad, update_price_request, get_price_request
from config import config

router = Router()

ADMIN_PASSWORD = "MARKAB777" # Siz xohlagan parol

@router.message(F.text == "🔐 Admin Panel")
async def admin_login(message: Message, state: FSMContext):
    await state.set_state(AdminAuth.waiting_for_password)
    await message.answer("🔑 <b>Admin panelga kirish uchun parolni kiriting:</b>", parse_mode="HTML", reply_markup=keyboards.get_main_menu())

@router.message(AdminAuth.waiting_for_password)
async def check_password(message: Message, state: FSMContext):
    if message.text == ADMIN_PASSWORD:
        await state.clear()
        await message.answer("🔓 <b>Xush kelibsiz, Admin!</b>\n\nFiliallarga mahsulot qo'shishingiz mumkin.", parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard())
    else:
        await message.answer("❌ <b>Parol noto'g'ri!</b> Qaytadan urinib ko'ring yoki bekor qiling.", parse_mode="HTML")

@router.message(F.text == "➕ Mahsulot qo'shish")
async def admin_add_product_start(message: Message, state: FSMContext):
    await state.set_state(AdminAddProduct.model)
    await message.answer("📱 <b>Qo'shmoqchi bo'lgan iPhone modelini tanlang:</b>", parse_mode="HTML", reply_markup=keyboards.get_iphone_models_keyboard())

@router.message(AdminAddProduct.model)
async def admin_add_model(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await message.answer("🏠 Admin menu", reply_markup=keyboards.get_admin_panel_keyboard())
        await state.clear()
        return
    await state.update_data(model=message.text)
    await state.set_state(AdminAddProduct.branch)
    branches = await get_all_branches()
    await message.answer("🏢 <b>Qaysi filialga qo'shmoqchisiz?</b>", parse_mode="HTML", reply_markup=keyboards.get_branches_keyboard(branches))

@router.message(AdminAddProduct.branch)
async def admin_add_branch(message: Message, state: FSMContext):
    await state.update_data(branch=message.text)
    await state.set_state(AdminAddProduct.storage)
    await message.answer("💾 <b>Xotira hajmini tanlang:</b>", parse_mode="HTML", reply_markup=keyboards.get_memory_keyboard())

@router.message(AdminAddProduct.storage)
async def admin_add_storage(message: Message, state: FSMContext):
    await state.update_data(storage=message.text)
    await state.set_state(AdminAddProduct.battery)
    await message.answer("🔋 <b>Batareya yomkostini kiriting (masalan: 95):</b>", parse_mode="HTML")

@router.message(AdminAddProduct.battery)
async def admin_add_battery(message: Message, state: FSMContext):
    await state.update_data(battery=message.text)
    await state.set_state(AdminAddProduct.condition)
    await message.answer("🛠 <b>Holatini tanlang:</b>", parse_mode="HTML", reply_markup=keyboards.get_condition_keyboard())

@router.message(AdminAddProduct.condition)
async def admin_add_condition(message: Message, state: FSMContext):
    await state.update_data(condition=message.text)
    await state.set_state(AdminAddProduct.price)
    await message.answer("💰 <b>Sotuv narxini kiriting (masalan: 8.5 mln yoki 800$):</b>", parse_mode="HTML")

@router.message(AdminAddProduct.price)
async def admin_add_price(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(AdminAddProduct.photos)
    await message.answer("📸 <b>Mahsulot rasmilarini yuboring (kamida 1 ta):</b>", parse_mode="HTML")

@router.message(AdminAddProduct.photos, F.photo)
async def admin_add_photos(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    data = await state.get_data()
    data['photos'] = [photo_id]
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

        phone_obj = await sync_to_async(Phone.objects.create)(
            model_name=model_name,
            memory=memory,
            battery_health=battery_val,
            color='Noma\'lum',
            price=price_val,
            condition='yangi' if data.get('condition') == 'ideal' else 'ishlatilgan',
            seller_phone=str(data.get('contact', '')),
            image=image_rel_path
        )
        with open('sync_debug.log', 'a') as f: f.write(f"DEBUG: Sync Bot -> Web App success! ID: {phone_obj.id}\n")
    except Exception as e:
        import traceback
        err_msg = f"DEBUG: Sync Bot -> Web App error: {e}\n{traceback.format_exc()}\n"
        with open('sync_debug.log', 'a') as f: f.write(err_msg)

    await message.answer("✅ <b>Mahsulot muvaffaqiyatli filialga va Mini Appga qo'shildi!</b>", parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard())
    await state.clear()

@router.message(F.text == "⬅️ Chiqish")
async def admin_exit(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🏠 Bosh menyuga qaytildi.", reply_markup=keyboards.get_main_menu())

@router.message(F.text == "🏢 Filiallarni boshqarish")
async def admin_branch_mgmt(message: Message, state: FSMContext):
    await message.answer("🏢 <b>Filiallarni boshqarish menyusi:</b>", parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard())

@router.message(F.text == "➕ Yangi filial qo'shish")
async def admin_add_branch_start(message: Message, state: FSMContext):
    await state.set_state(AdminBranchMgmt.waiting_for_name)
    await message.answer("📝 <b>Yangi filial nomini kiriting:</b>", parse_mode="HTML")

@router.message(AdminBranchMgmt.waiting_for_name)
async def admin_add_branch_process(message: Message, state: FSMContext):
    await add_branch(message.text)
    await message.answer(f"✅ <b>{message.text}</b> filiali muvaffaqiyatli qo'shildi!", parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard())
    await state.clear()

@router.message(F.text == "❌ Filialni o'chirish")
async def admin_delete_branch_start(message: Message, state: FSMContext):
    branches = await get_all_branches()
    await state.set_state(AdminBranchMgmt.waiting_for_delete)
    await message.answer("🗑 <b>O'chirmoqchi bo'lgan filialni tanlang:</b>", parse_mode="HTML", reply_markup=keyboards.get_branches_keyboard(branches))

@router.message(AdminBranchMgmt.waiting_for_delete)
async def admin_delete_branch_process(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await admin_branch_mgmt(message, state)
        return
    await delete_branch(message.text)
    await message.answer(f"✅ <b>{message.text}</b> filiali o'chirildi!", parse_mode="HTML", reply_markup=keyboards.get_admin_branch_mgmt_keyboard())
    await state.clear()

@router.message(F.text == "⬅️ Admin menyuga qaytish")
async def admin_return(message: Message, state: FSMContext):
    await message.answer("🏠 Admin panel", reply_markup=keyboards.get_admin_panel_keyboard())

@router.message(F.text == "🗑 Mahsulotni o'chirish")
async def admin_delete_product_start(message: Message, state: FSMContext):
    await state.set_state(AdminDeleteProduct.waiting_for_model)
    await message.answer("📱 <b>Qaysi modeldagi telefonni o'chirmoqchisiz?</b>\n(Masalan: iPhone 13 Pro Max)", parse_mode="HTML")

@router.message(AdminDeleteProduct.waiting_for_model)
async def admin_delete_product_model(message: Message, state: FSMContext):
    model = message.text
    # Search in Bot DB
    import sqlite3
    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, model, storage, price FROM ads WHERE model LIKE ?", (f"%{model}%",))
    ads = cursor.fetchall()
    conn.close()
    
    if not ads:
        await message.answer("❌ <b>Bunday modeldagi mahsulot topilmadi.</b>", parse_mode="HTML")
        return
    
    text = "🔍 <b>Topilgan mahsulotlar:</b>\n\n"
    for ad in ads:
        text += f"🆔 {ad[0]} | {ad[1]} {ad[2]}GB | {ad[3]:,.0f} so'm\n"
    
    text += "\n🔢 <b>O'chirmoqchi bo'lgan telefon ID sini kiriting:</b>"
    await state.set_state(AdminDeleteProduct.waiting_for_selection)
    await message.answer(text, parse_mode="HTML")

@router.message(AdminDeleteProduct.waiting_for_selection)
async def admin_delete_product_finish(message: Message, state: FSMContext):
    try:
        ad_id = int(message.text)
        await delete_ad(ad_id)
        await message.answer(f"✅ <b>ID {ad_id}</b> bo'lgan mahsulot o'chirildi!", parse_mode="HTML", reply_markup=keyboards.get_admin_panel_keyboard())
        await state.clear()
    except ValueError:
        await message.answer("❌ <b>Iltimos, faqat ID raqamini kiriting.</b>")

@router.callback_query(F.data.startswith("approve_"))
async def approve_ad(callback: CallbackQuery, state: FSMContext):
    ad_id = int(callback.data.split("_")[1])
    await state.update_data(ad_id=ad_id)
    await state.set_state(AdminState.setting_branch)
    branches = await get_all_branches()
    await callback.message.answer("🏢 <b>Ushbu e'lon qaysi filialga tegishli?</b>", parse_mode="HTML", reply_markup=keyboards.get_branches_keyboard(branches))
    await callback.answer()

@router.message(AdminState.setting_branch)
async def process_admin_branch(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    
    data = await state.get_data()
    ad_id = data['ad_id']
    branch = message.text
    
    await update_ad_status(ad_id, "approved", branch=branch)
    ad = await get_ad_by_id(ad_id)
    
    await message.bot.send_message(ad['user_id'], f"✅ <b>Tabriklaymiz!</b>\n\nSizning e'loningiz (ID: {ad_id}) tasdiqlandi va <b>{branch}</b> filialiga biriktirildi. 🚀", parse_mode="HTML")
    await message.answer(f"✅ E'lon {ad_id} tasdiqlandi va {branch} ga qo'shildi.", reply_markup=keyboards.get_main_menu())
    await state.clear()

@router.callback_query(F.data.startswith("reject_"))
async def reject_ad(callback: CallbackQuery):
    ad_id = int(callback.data.split("_")[1])
    await update_ad_status(ad_id, "rejected")
    ad = await get_ad_by_id(ad_id)
    await callback.message.bot.send_message(ad['user_id'], f"❌ <b>Afsuski...</b>\n\nSizning e'loningiz (ID: {ad_id}) rad etildi. Ma'lumotlarni tekshirib qaytadan urinib ko'ring.", parse_mode="HTML")
    await callback.message.edit_text(f"❌ E'lon {ad_id} rad etildi.")
    await callback.answer()

@router.callback_query(F.data.startswith("setprice_"))
async def admin_set_price(callback: CallbackQuery, state: FSMContext):
    req_id = int(callback.data.split("_")[1])
    await state.update_data(req_id=req_id)
    await state.set_state(AdminState.setting_price)
    await callback.message.answer("💰 <b>Tasdiqlangan narxni kiriting (mln so'mda):</b>", parse_mode="HTML")
    await callback.answer()

@router.message(AdminState.setting_price)
async def process_admin_price(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID: return
    
    data = await state.get_data()
    req_id = data['req_id']
    price = message.text
    
    await update_price_request(req_id, price)
    req = await get_price_request(req_id)
    
    await message.bot.send_message(req['user_id'], f"📢 <b>Admin tomonidan tasdiqlangan narx:</b>\n\n📱 Model: {req['model']}\n💰 Yakuniy narx: <b>{price} mln so'm</b>\n\nSotishni xohlasangiz 'Telefon sotish' bo'limiga o'ting! 🚀", parse_mode="HTML")
    await message.answer("✅ Foydalanuvchiga narx yuborildi.", reply_markup=keyboards.get_main_menu())
    await state.clear()
