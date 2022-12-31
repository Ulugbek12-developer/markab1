from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu, get_branches_keyboard, get_language_keyboard, get_subscription_keyboard
from database import update_user_language, get_user_language, get_all_branches
from strings import STRINGS

router = Router()

CHANNEL_ID = "@markab_electronics"

async def check_user_sub(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(STRINGS['uz']['start_welcome'], reply_markup=get_language_keyboard())

@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    await update_user_language(callback.from_user.id, lang)
    
    is_sub = await check_user_sub(callback.bot, callback.from_user.id)
    if is_sub:
        await callback.message.edit_text(STRINGS[lang]['main_menu'])
        await callback.message.answer("🎉", reply_markup=get_main_menu(lang))
    else:
        await callback.message.edit_text(STRINGS[lang]['sub_required'], reply_markup=get_subscription_keyboard(lang))

@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery):
    lang = await get_user_language(callback.from_user.id)
    is_sub = await check_user_sub(callback.bot, callback.from_user.id)
    
    if is_sub:
        await callback.message.delete()
        await callback.message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
    else:
        await callback.answer(STRINGS[lang]['sub_error'], show_alert=True)

@router.message(F.text.in_(["ℹ️ Ma'lumot/Yordam", "ℹ️ Инфо/Помощь"]))
async def cmd_info(message: Message):
    lang = await get_user_language(message.from_user.id)
    if lang == 'uz':
        text = (
            "🤖 <b>MobiTrade iPhone Bot</b> 🌟\n\n"
            "✅ Faqat original iPhone qurilmalari\n"
            "✅ Professional baholash tizimi\n"
            "✅ 7 ta filial bo'ylab xizmat ko'rsatish\n"
            "🛠 <i>Muammolar bo'lsa:</i> @markab_admin 👨‍💻"
        )
    else:
        text = (
            "🤖 <b>MobiTrade iPhone Bot</b> 🌟\n\n"
            "✅ Только оригинальные устройства iPhone\n"
            "✅ Профессиональная система оценки\n"
            "✅ Обслуживание в 7 филиалах\n"
            "🛠 <i>Если возникли проблемы:</i> @markab_admin 👨‍💻"
        )
    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@router.message(F.text.in_(["🏢 Bizning filiallar", "🏢 Наши филиалы"]))
async def cmd_branches(message: Message):
    lang = await get_user_language(message.from_user.id)
    branches = await get_all_branches()
    
    if lang == 'uz':
        text = "📍 <b>Bizning filiallarimiz:</b>\n\n"
        prompt = "\n👇 <i>Filialni tanlab batafsil ma'lumot oling:</i>"
    else:
        text = "📍 <b>Наши филиалы:</b>\n\n"
        prompt = "\n👇 <i>Выберите филиал для подробной информации:</i>"
        
    for b in branches:
        text += f"🏬 <b>{b['name']}</b>\n"
    
    text += prompt
    await message.answer(text, parse_mode="HTML", reply_markup=get_branches_keyboard(branches, lang))

@router.message(F.text.in_(["⬅️ Orqaga", "⬅️ Назад"]))
async def cmd_back(message: Message, state: FSMContext):
    lang = await get_user_language(message.from_user.id)
    await message.answer(STRINGS[lang]['main_menu'], reply_markup=get_main_menu(lang))
    await state.clear()

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    lang = await get_user_language(message.from_user.id)
    await state.clear()
    await message.answer(STRINGS[lang]['msg_cancelled'], reply_markup=get_main_menu(lang))
