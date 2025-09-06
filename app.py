from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import button as bt
from simple_func import add_users, list_institution
router = Router()

#команда /start
@router.message(CommandStart())
async def start(message: types.Message):
    user_info = message.from_user
    add_users(user_info)
    await message.answer("Привіт, я емулятор термального принтеру", reply_markup=bt.main)
    
@router.message(F.text == "/check")
async def list(message:Message):
    await message.answer(list_institution(), reply_markup=bt.main)



@router.message(F.text == "Файл останнього чеку")
async def get_file(message:Message):
    file_path = "printer_checks.txt"   # шлях до файлу
    try:
        await message.answer_document(types.FSInputFile(file_path), reply_markup=bt.main)
    except Exception as e:
        await message.answer(f"❌ Не вдалося відправити файл: {e}")
        
@router.message(F.text == "Останній чек")
async def get_file(message:Message):
    with open("printer_checks.txt", "r", encoding='utf-8') as f:
                last_check = f.read()
    await message.answer(f"🖨 Останній чек:\n\n```\n{last_check}\n```", parse_mode="Markdown", reply_markup=bt.main)




