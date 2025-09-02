import asyncio
import threading
import logging

from aiogram import Bot, Dispatcher

from tok import TOKEN
from app import router
from printer import printer_server

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    # Додаємо router
    dp.include_router(router)
    
    threading.Thread(target=printer_server, daemon=True).start()

    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("Polling зупинено")
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Запускаємо головну функцію
    asyncio.run(main())