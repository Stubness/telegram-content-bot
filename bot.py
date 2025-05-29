import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers.user_submission import register_handlers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    print("🤖 Bot is running...")
    register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
