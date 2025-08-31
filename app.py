from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from simple_func import check_subscribe, delete_user
router = Router()

#команда /start
@router.message(CommandStart())
async def start(message:types.Message):
    user_id = message.from_user.id
    await message.answer(check_subscribe(user_id))
    
#команда /unsub    
@router.message(Command('unsub'))
async def unsub(message:types.Message):
    user_id = message.from_user.id
    delete_user(user_id, "subscribet_ID.txt")
    await message.answer( "Ви успішно відписалися від отримання нових чеків, для підписки натисніть /start")
    
#команда /file
@router.message(Command('file'))
async def get_file(message:types.Message):
    file_path = "printer_checks.txt"   # шлях до файлу
    try:
        await message.answer_document(types.FSInputFile(file_path))
    except Exception as e:
        await message.answer(f"❌ Не вдалося відправити файл: {e}")
        
#команда /print
@router.message(Command('print'))
async def get_file(message:types.Message):
    with open("printer_checks.txt", "r", encoding='utf-8') as f:
                last_check = f.read()
    await message.answer(f"🖨 Останній чек:\n\n```\n{last_check}\n```", parse_mode="Markdown")




