# bot.py

import discord
from discord.ext import commands
import asyncio
import logging
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    await bot.load_extension("commands.alerts")
async def main():
    async with bot:
        await load_extensions()
        
        from tasks.stock_checker import setup_stock_checker
        setup_stock_checker(bot)

        await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
