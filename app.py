from flask import Flask, request, abort
import hashlib
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import telegram

app = Flask(__name__)

# Переменные окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
FEEKASSA_SECRET = os.getenv("FEEKASSA_SECRET")

# Настройка Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google_creds.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# Настройка Telegram
bot = telegram.Bot(token=BOT_TOKEN)

@app.route("/freekassa-webhook", methods=["POST"])
def freekassa_webhook():
    data = request.form.to_dict()
    received_sign = data.pop("sign", "")

    # Подпись
    sorted_data = sorted(data.items())
    sign_string = ":".join([v for k, v in sorted_data]) + ":" + FEEKASSA_SECRET
    generated_sign = hashlib.md5(sign_string.encode()).hexdigest()

    if received_sign != generated_sign:
        abort(403)

    # Логика при успешном платеже
    bot.send_message(chat_id=TG_CHAT_ID, text=f"💰 Поступление оплаты: {data.get('AMOUNT')} {data.get('CURRENCY')}")
    sheet.append_row([data.get("MERCHANT_ORDER_ID"), data.get("AMOUNT"), data.get("CURRENCY")])

    return "YES"

@app.route("/", methods=["GET"])
def root():
    return "Freekassa bot running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
