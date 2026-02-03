import telebot
from flask import Flask, request, abort
import re
import random
import requests
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get('BOT_TOKEN', '8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE')
ADMIN_ID = int(os.environ.get('ADMIN_ID', '6751771375'))

bot = telebot.TeleBot(BOT_TOKEN)

GATES = [
    "https://httpbin.org/post",
    "https://jsonplaceholder.typicode.com/posts",
    "https://postman-echo.com/post"
]

def luhn_checksum(card_number):
    digits = [int(d) for d in card_number]
    odd = digits[-1::-2]
    even = digits[-2::-2]
    checksum = sum(odd)
    checksum += sum(sum(divmod(d*2, 10)) for d in even)
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
    data = {'cardNumber': num, 'expMonth': mon, 'expYear': yr, 'cvc': cvv}
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone)', 'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        r = requests.post(random.choice(GATES), data=data, headers=headers, timeout=8)
        return f"🔥 LIVE ({r.status_code})" if r.status_code < 400 else f"❌ DEAD ({r.status_code})"
    except:
        return "⚠️ ERROR"

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 
        "🔥 **CC KILLER FREE WEBHOOK v2026** 🔥\n\n"
        "Send CCs:\n"
        "`4111111111111111|12|28|123`\n"
        "`4532 0151 1283 0366 |12|28|123`\n\n"
        "**FREE 24/7 Render** 💀")

@bot.message_handler(func=lambda m: True)
def checker(message):
    ccs = [parse_cc(line) for line in message.text.split('\n') if parse_cc(line)]
    if not ccs:
        bot.reply_to(message, "❌ No CCs")
        return
    bot.reply_to(message, f"🔥 **{len(ccs)}** CCs...")
    for cc in ccs[:50]:
        result = check_cc(cc)
        bot.reply_to(message, f"`{cc}` → **{result}**")

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route('/')
def index():
    return "🔥 CC KILLER LIVE ON RENDER!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://your-render-url.onrender.com/{8268191244:AAFVk-Y-T3wmCt25otqjZj_ol6vqgwknWLE}")
    app.run(host='0.0.0.0', port=port)
