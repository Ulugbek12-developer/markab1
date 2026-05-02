from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import BuyPhone
from keyboards import get_iphone_models_keyboard, get_branches_keyboard, get_main_menu, get_confirm_keyboard, get_back_keyboard, get_payment_type_keyboard, get_location_keyboard, get_installment_plan_keyboard
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
        
    model = message.text
    await state.update_data(model=model)
    
    results = await search_ads(model=model, branch=None)
    
    if not results:
        err_msg = STRINGS[lang]['no_results'].replace('{branch} filialida ', '').replace('в {branch} филиале ', '')
        await message.answer(err_msg.format(branch='', model=model), parse_mode="HTML", reply_markup=get_main_menu(lang))
        await state.clear()
    else:
        title_msg = STRINGS[lang]['results_title'].replace('{branch} filialidagi', 'Barcha filiallardagi').replace('В {branch} филиале', 'Во всех филиалах')
        await message.answer(title_msg.format(branch='', model=model), parse_mode="HTML")
        ids = []
        s = STRINGS[lang]
        for row in results:
            branch_name = row['branch'].capitalize() if row['branch'] else 'Malika'
            summary = (
                f"🆔 <b>ID: {row['id']}</b>\n"
                f"📱 <b>{s['lbl_model']}:</b> {row['model']}\n"
                f"💾 <b>{s['lbl_memory']}:</b> {row['storage']}\n"
                f"🔋 <b>{s['lbl_battery']}:</b> {row['battery']}%\n"
                f"🛠 <b>{s['lbl_condition']}:</b> {row['condition']}\n"
                f"💰 <b>{s['lbl_price']}:</b> {int(row['price']):,.0f} so'm\n"
                f"📍 <b>{s['btn_branches'].replace('🏢 ', '')}:</b> {branch_name}"
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
        
        await state.update_data(available_ids=ids, results_cache=[dict(r) for r in results])
        await state.set_state(BuyPhone.select_id)
        await message.answer(STRINGS[lang]['prompt_select_id'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))

@router.message(BuyPhone.select_id)
async def process_select_id(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    if message.text in [STRINGS[lang]['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.model)
        await message.answer(STRINGS[lang]['prompt_buy_model'], reply_markup=get_iphone_models_keyboard(lang))
        return

    data = await state.get_data()
    if message.text not in data.get('available_ids', []):
        await message.answer(STRINGS[lang]['err_id'])
        return

    await state.update_data(selected_id=message.text)
    
    # Store selected price for installment calculations
    # Find the price of the selected ad
    selected_price_str = "0"
    for row in data.get('results_cache', []):
        if str(row['id']) == message.text:
            selected_price_str = row['price']
            break
            
    # Clean price string and convert to float
    import re
    price_digits = re.findall(r'\d+', str(selected_price_str))
    price_val = int(''.join(price_digits)) if price_digits else 0
    await state.update_data(selected_price=price_val)

    await state.set_state(BuyPhone.payment_type)
    from keyboards import get_payment_type_keyboard
    await message.answer(STRINGS[lang]['prompt_payment_type'], parse_mode="HTML", reply_markup=get_payment_type_keyboard(lang))

@router.message(BuyPhone.payment_type)
async def process_payment_type(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text in [s['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.select_id)
        await message.answer(s['prompt_select_id'], parse_mode="HTML", reply_markup=get_back_keyboard(lang))
        return

    if message.text == s['btn_cash']:
        await state.update_data(payment_type="cash")
        await state.set_state(BuyPhone.confirm)
        data = await state.get_data()
        await message.answer(s['confirm_buy'].format(id=data['selected_id']), parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))
    
    elif message.text == s['btn_installment']:
        await state.update_data(payment_type="installment")
        await state.set_state(BuyPhone.location)
        from keyboards import get_location_keyboard
        await message.answer(s['prompt_location'], parse_mode="HTML", reply_markup=get_location_keyboard(lang))
    else:
        await message.answer(s['prompt_payment_type'])

@router.message(BuyPhone.location)
async def process_location(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text in [s['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.payment_type)
        from keyboards import get_payment_type_keyboard
        await message.answer(s['prompt_payment_type'], parse_mode="HTML", reply_markup=get_payment_type_keyboard(lang))
        return

    if message.text not in [s['btn_city'], s['btn_region']]:
        from keyboards import get_location_keyboard
        await message.answer(s['prompt_location'], parse_mode="HTML", reply_markup=get_location_keyboard(lang))
        return

    location_type = "shahar" if message.text == s['btn_city'] else "viloyat"
    await state.update_data(location=location_type)
    
    data = await state.get_data()
    price = float(data.get('selected_price', 0))
    
    initial_percent = 0.3 if location_type == "shahar" else 0.4
    initial = price * initial_percent
    remaining = price - initial
    
    m3 = remaining / 3 * 1.10
    m6 = remaining / 6 * 1.15
    m12 = remaining / 12 * 1.25
    
    await state.update_data(initial=initial, m3=m3, m6=m6, m12=m12)
    
    summary = (
        f"📊 <b>Muddatli to'lov ma'lumoti:</b>\n\n"
        f"💰 Umumiy narx: <b>{price:,.0f} so'm</b>\n"
        f"💳 Boshlang'ich to'lov ({int(initial_percent*100)}%): <b>{initial:,.0f} so'm</b>\n\n"
    )
    
    await state.set_state(BuyPhone.installment_plan)
    from keyboards import get_installment_plan_keyboard
    await message.answer(summary + s['prompt_plan'], parse_mode="HTML", reply_markup=get_installment_plan_keyboard(m3, m6, m12, lang))

@router.message(BuyPhone.installment_plan)
async def process_installment_plan(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text in [s['btn_back'], "⬅️ Orqaga", "⬅️ Назад"]:
        await state.set_state(BuyPhone.location)
        from keyboards import get_location_keyboard
        await message.answer(s['prompt_location'], parse_mode="HTML", reply_markup=get_location_keyboard(lang))
        return

    await state.update_data(plan_selected=message.text)
    await state.set_state(BuyPhone.confirm)
    
    data = await state.get_data()
    await message.answer(s['confirm_buy'].format(id=data['selected_id']), parse_mode="HTML", reply_markup=get_confirm_keyboard(lang))

@router.message(BuyPhone.confirm)
async def process_buy_confirm(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    s = STRINGS[lang]
    if message.text == s['btn_confirm']:
        data = await state.get_data()
        
        payment_info = "Naqd to'lov"
        if data.get('payment_type') == "installment":
            loc_text = "Shahar (30%)" if data.get('location') == "shahar" else "Viloyat (40%)"
            payment_info = (
                f"Muddatli to'lov\n"
                f"Hudud: {loc_text}\n"
                f"Boshlang'ich: {data.get('initial', 0):,.0f} so'm\n"
                f"Tanlangan reja: {data.get('plan_selected', '')}"
            )
        
        if config.ADMIN_ID:
            await message.bot.send_message(
                config.ADMIN_ID, 
                f"🛍 <b>YANGI ZAKAZ!</b>\n\n"
                f"User: {message.from_user.full_name}\n"
                f"Telefon ID: {data['selected_id']}\n"
                f"Model: {data['model']}\n"
                f"Filial: {data.get('branch')}\n"
                f"To'lov: {payment_info}",
                parse_mode="HTML"
            )
        
        await message.answer(s['buy_success'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    elif message.text == s['btn_back']:
        data = await state.get_data()
        if data.get('payment_type') == "installment":
            await state.set_state(BuyPhone.installment_plan)
            from keyboards import get_installment_plan_keyboard
            await message.answer(s['prompt_plan'], parse_mode="HTML", reply_markup=get_installment_plan_keyboard(data['m3'], data['m6'], data['m12'], lang))
        elif data.get('payment_type') == "cash":
            await state.set_state(BuyPhone.payment_type)
            from keyboards import get_payment_type_keyboard
            await message.answer(s['prompt_payment_type'], parse_mode="HTML", reply_markup=get_payment_type_keyboard(lang))
        else:
            await state.set_state(BuyPhone.select_id)
            from keyboards import get_back_keyboard
            await message.answer(s['prompt_select_id'], reply_markup=get_back_keyboard(lang))
        return
    else:
        await message.answer(s['msg_cancelled'], parse_mode="HTML", reply_markup=get_main_menu(lang))
    
    await state.clear()
