import asyncio
import threading
import logging

from aiogram import Bot, Dispatcher

from tok import TOKEN
from app import router
from printer import printer_server

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def on_startup():
    print("Запуск системи...")
    # Запускаємо принтерний сервер у потоці
    threading.Thread(target=printer_server, daemon=True).start()

async def main():
    # Додаємо router
    dp.include_router(router)
    
    # Викликаємо on_startup
    await on_startup()
    
    # запускаємо polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Запускаємо головну функцію
    asyncio.run(main())