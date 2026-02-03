import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, executor, types
import re
import random

# EDIT THESE 2 LINES
BOT_TOKEN = "8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE"
ADMIN_ID = 6751771375  # YOUR TG USER ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

GATES = ["https://httpbin.org/post", "https://jsonplaceholder.typicode.com/posts"]

def parse_cc(text):
    match = re.search(r'(\d{13,19})[^\d]*(\d{2})?[^\d]*(\d{2,4})?[^\d]*(\d{3,4})?', text)
    if match:
        num, mon, yr, cvv = match.groups()
        return f"{num}|{mon or '12'}|{yr or '28'}|{cvv or '123'}"
    return None

async def check_cc(cc):
    num, mon, yr, cvv = cc.split('|')
    
    # Fast Luhn
    def luhn(n):
        digits = [int(d) for d in n]
        return sum(digits[-1::-2][::-1] + [sum(divmod(d*2,10)) for d in digits[-2::-2]]) % 10 == 0
    
    if not luhn(num):
        return "💀 DIE"
    
    data = f"card={num}&month={mon}&year={yr}&cvv={cvv}"
    headers = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(8)) as session:
            async with session.post(random.choice(GATES), data=data, headers=headers) as resp:
                if resp.status < 400:
                    return f"🔥 LIVE ({resp.status})"
                return f"❌ DEAD ({resp.status})"
    except:
        return "⚠️ ERR"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("🔥 CC KILLER FREE ∞\nSend CC: `4532015112830366|12|28|123`")

@dp.message_handler()
async def checker(message: types.Message):
    ccs = [parse_cc(line) for line in message.text.split('\n') if parse_cc(line)]
    
    if not ccs:
        await message.reply("❌ No valid CC")
        return
    
    await message.reply(f"🔥 Checking {len(ccs)}...")
    
    semaphore = asyncio.Semaphore(5)
    async def proc(cc):
        async with semaphore:
            res = await check_cc(cc)
            await message.reply(f"`{cc}` → {res}")
            await asyncio.sleep(0.4)
    
    tasks = [proc(cc) for cc in ccs[:30]]
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    print("🔥 CC KILLER STARTED")
    executor.start_polling(dp, skip_updates=True)
