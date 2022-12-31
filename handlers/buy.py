from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import BuyPhone
from keyboards import get_iphone_models_keyboard, get_branches_keyboard, get_main_menu, get_confirm_keyboard
from database import search_ads
from config import config

router = Router()

from database import search_ads, get_user_language, get_all_branches
from config import config
from strings import STRINGS

router = Router()

@router.message(F.text.in_(["🛍 Telefon sotib olish", "🛍 Купить телефон"]))
async def start_buy(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await state.set_state(BuyPhone.model)
    await message.answer(STRINGS[lang]['prompt_buy_model'], parse_mode="HTML", reply_markup=get_iphone_models_keyboard(lang))

@router.message(BuyPhone.model)
async def process_buy_model(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.clear()
        await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
        return

    await state.update_data(model=message.text)
    await state.set_state(BuyPhone.branch)
    branches = await get_all_branches()
    await message.answer(STRINGS[lang]['prompt_buy_branch'], parse_mode="HTML", reply_markup=get_branches_keyboard(branches, lang))

@router.message(BuyPhone.branch)
async def process_buy_branch(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.model)
        await message.answer(STRINGS[lang]['prompt_buy_model'], reply_markup=get_iphone_models_keyboard(lang))
        return

    branch = message.text
    data = await state.get_data()
    model = data['model']
    
    results = await search_ads(model=model, branch=branch)
    
    if not results:
        await message.answer(STRINGS[lang]['no_results'].format(branch=branch, model=model), parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    else:
        await message.answer(STRINGS[lang]['results_title'].format(branch=branch, model=model), parse_mode="HTML")
        ids = []
        s = STRINGS[lang]
        for row in results:
            summary = (
                f"🆔 <b>ID: {row['id']}</b>\n"
                f"📱 <b>{s['lbl_model']}:</b> {row['model']}\n"
                f"💾 <b>{s['lbl_memory']}:</b> {row['storage']}\n"
                f"🔋 <b>{s['lbl_battery']}:</b> {row['battery']}%\n"
                f"🛠 <b>{s['lbl_condition']}:</b> {row['condition']}\n"
                f"💰 <b>{s['lbl_price']}:</b> {row['price']}\n"
                f"📍 <b>{s['btn_branches'].replace('🏢 ', '')}:</b> {row['branch']}"
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
        await message.answer(STRINGS[lang]['prompt_select_id'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(BuyPhone.select_id)
async def process_select_id(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.branch)
        branches = await get_all_branches()
        await message.answer(STRINGS[lang]['prompt_buy_branch'], reply_markup=get_branches_keyboard(branches, lang))
        return

    data = await state.get_data()
    if message.text not in data.get('available_ids', []):
        await message.answer(STRINGS[lang]['err_id'])
        return

    await state.update_data(selected_id=message.text)
    await state.set_state(BuyPhone.confirm)
    await message.answer(STRINGS[lang]['confirm_buy'].format(id=message.text), parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))

@router.message(BuyPhone.confirm)
async def process_buy_confirm(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text == s['btn_confirm']:
        data = await state.get_data()
        if config.ADMIN_ID:
            await message.bot.send_message(
                config.ADMIN_ID, 
                f"🛍 <b>YANGI ZAKAZ!</b>\n\nUser: {message.from_user.full_name}\nTelefon ID: {data['selected_id']}\nModel: {data['model']}",
                parse_mode="HTML"
            )
        
        await message.answer(s['buy_success'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    elif message.text == s['btn_back']:
        await state.set_state(BuyPhone.select_id)
        await message.answer(s['prompt_select_id'], reply_markup=get_back_keyboard(lang))
        return
    else:
        await message.answer(s['msg_cancelled'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    
    await state.clear()
