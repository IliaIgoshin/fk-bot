import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Авторизация и подключение к Google Sheet
def get_sheet():
    creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    sheet_id = os.environ["GOOGLE_SHEET_ID"]
    sheet = client.open_by_key(sheet_id).sheet1
    return sheet

# Добавление строки данных в таблицу
def append_payment(data: list):
    try:
        sheet = get_sheet()
        sheet.append_row(data)
    except Exception as e:
        print(f"[Google Sheets Error] {e}")
