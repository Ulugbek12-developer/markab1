from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu, get_branches_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🎉")
    await message.answer(
        "👋 <b>Assalomu alaykum!</b>\n\n"
        "✨ <b>MobiTrade</b> premium iPhone botiga xush kelibsiz! 🎊\n"
        "📱 <i>Bu yerda siz iPhone sotishingiz, narxlatishingiz yoki sotib olishingiz mumkin.</i> 🚀\n\n"
        "👇 <b>Quyidagi menyudan kerakli bo'limni tanlang:</b>",
        parse_mode="HTML",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "ℹ️ Ma'lumot/Yordam")
async def cmd_info(message: Message):
    await message.answer(
        "🤖 <b>MobiTrade iPhone Bot</b> 🌟\n\n"
        "✅ Faqat original iPhone qurilmalari\n"
        "✅ Professional baholash tizimi\n"
        "✅ 7 ta filial bo'ylab xizmat ko'rsatish\n"
        "✅ 🌐 <a href='https://markab.pythonanywhere.com/'>Premium Mini App</a> mavjud\n\n"
        "🛠 <i>Muammolar bo'lsa:</i> @admin_username 👨‍💻",
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@router.message(F.text == "🏢 Bizning filiallar")
async def cmd_branches(message: Message):
    from database import get_all_branches
    branches = await get_all_branches()
    text = "📍 <b>Bizning filiallarimiz:</b>\n\n"
    for b in branches:
        text += f"🏬 <b>{b['name']}</b>\n"
    
    text += "\n👇 <i>Filialni tanlab batafsil ma'lumot oling:</i>"
    await message.answer(text, parse_mode="HTML", reply_markup=get_branches_keyboard(branches))

@router.message(F.text == "🌐 Mini App")
async def cmd_webapp(message: Message):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Mini Appni ochish", web_app=WebAppInfo(url="https://markab.pythonanywhere.com/"))]
    ])
    
    await message.answer(
        "🌐 <b>Bizning premium Mini Appimiz tayyor!</b>\n\n"
        "📱 <i>Bu yerda siz barcha iPhone modellarini ko'rishingiz va buyurtma berishingiz mumkin.</i>\n\n"
        "👇 <b>Pastdagi tugmani bosing:</b>",
        parse_mode="HTML",
        reply_markup=kb
    )

@router.message(F.text == "⬅️ Orqaga")
async def cmd_back(message: Message, state: FSMContext):
    await message.answer("🏠 <b>Bosh sahifa</b>", parse_mode="HTML", reply_markup=get_main_menu())
    await state.clear()

@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("🚫 Amal bekor qilindi.", reply_markup=get_main_menu())
