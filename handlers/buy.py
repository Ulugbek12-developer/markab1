from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import BuyPhone
from keyboards import get_iphone_models_keyboard, get_branches_keyboard, get_main_menu, get_confirm_keyboard
from database import search_ads
from config import config

router = Router()

@router.message(F.text == "🛍 Telefon sotib olish")
async def start_buy(message: Message, state: FSMContext):
    await state.set_state(BuyPhone.model)
    await message.answer("📲 <b>Qaysi modeldagi iPhone qidiryapsiz?</b>", parse_mode="HTML", reply_markup=get_iphone_models_keyboard())

@router.message(BuyPhone.model)
async def process_buy_model(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer("🏠 Asosiy menyu", reply_markup=get_main_menu())
        return

    await state.update_data(model=message.text)
    await state.set_state(BuyPhone.branch)
    from database import get_all_branches
    branches = await get_all_branches()
    await message.answer("🏢 <b>Qaysi filialdan sotib olmoqchisiz?</b>", parse_mode="HTML", reply_markup=get_branches_keyboard(branches))

@router.message(BuyPhone.branch)
async def process_buy_branch(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":
        await state.set_state(BuyPhone.model)
        await message.answer("📲 iPhone modelini tanlang:", reply_markup=get_iphone_models_keyboard())
        return

    branch = message.text
    data = await state.get_data()
    model = data['model']
    
    results = await search_ads(model=model, branch=branch)
    
    if not results:
        await message.answer(f"❌ Afsuski, <b>{branch}</b> filialida <b>{model}</b> topilmadi.", parse_mode="HTML", reply_markup=get_main_menu())
        await state.clear()
    else:
        await message.answer(f"🔎 <b>{branch}</b> filialidagi <b>{model}</b> modellari:", parse_mode="HTML")
        ids = []
        for row in results:
            summary = (
                f"🆔 <b>ID: {row['id']}</b>\n"
                f"📱 <b>Model:</b> {row['model']}\n"
                f"💾 <b>Xotira:</b> {row['storage']}\n"
                f"🔋 <b>Batareya:</b> {row['battery']}%\n"
                f"🛠 <b>Holati:</b> {row['condition']}\n"
                f"💰 <b>Narxi:</b> {row['price']}\n"
                f"📍 <b>Filial:</b> {row['branch']}"
            )
            photo_list = [p for p in row['photos'].split(",") if p] if row['photos'] else []
            if photo_list:
                try:
                    await message.answer_photo(photo_list[0], caption=summary, parse_mode="HTML")
                except Exception:
                    await message.answer(summary, parse_mode="HTML")
            else:
                await message.answer(summary, parse_mode="HTML")
            ids.append(str(row['id']))
        
        await state.update_data(available_ids=ids)
        await state.set_state(BuyPhone.select_id)
        await message.answer("📝 <b>Sotib olmoqchi bo'lgan telefon ID sini yozing:</b>", parse_mode="HTML")

@router.message(BuyPhone.select_id)
async def process_select_id(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.text not in data.get('available_ids', []):
        await message.answer("❌ Noto'g'ri ID. Iltimos, yuqoridagi ro'yxatdan ID tanlang:")
        return

    await state.update_data(selected_id=message.text)
    await state.set_state(BuyPhone.confirm)
    await message.answer(f"❓ <b>ID {message.text} bo'lgan telefonni buyurtma qilishni tasdiqlaysizmi?</b>", parse_mode="HTML", reply_markup=get_confirm_keyboard())

@router.message(BuyPhone.confirm)
async def process_buy_confirm(message: Message, state: FSMContext):
    if message.text == "✅ Tasdiqlash":
        data = await state.get_data()
        if config.ADMIN_ID:
            await message.bot.send_message(
                config.ADMIN_ID, 
                f"🛍 <b>YANGI ZAKAZ!</b>\n\nUser: {message.from_user.full_name}\nTelefon ID: {data['selected_id']}\nModel: {data['model']}",
                parse_mode="HTML"
            )
        
        await message.answer("✅ <b>Buyurtmangiz qabul qilindi!</b>\nAdmin tez orada siz bilan bog'lanadi.", parse_mode="HTML", reply_markup=get_main_menu())
    else:
        await message.answer("🚫 <b>Bekor qilindi.</b>", parse_mode="HTML", reply_markup=get_main_menu())
    
    await state.clear()
