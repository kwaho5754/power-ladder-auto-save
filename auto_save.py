import requests
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pytz
import os

# === 구글 시트 인증 ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_content = json.loads(os.getenv("GOOGLE_SHEET_JSON"))
credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_content, scope)
gc = gspread.authorize(credentials)

# === 시트 열기 ===
spreadsheet = gc.open("실시간결과")
worksheet = spreadsheet.worksheet("예측결과")

# === 기존 회차 목록 불러오기 ===
existing_rounds = worksheet.col_values(2)[1:]  # 2번째 열 = 회차
existing_rounds = list(map(int, existing_rounds)) if existing_rounds else []

# === 24시간 전 기준 시간 계산 ===
now = datetime.now(pytz.timezone("Asia/Seoul"))
yesterday = now - timedelta(days=1)

# === 실시간 데이터 불러오기 ===
url = "https://ntry.com/data/json/games/power_ladder/result.json"
response = requests.get(url)
data = response.json()

# === 필터링 및 저장할 행 만들기 ===
new_rows = []
for item in data:
    try:
        item_date = datetime.strptime(item['reg_date'], '%Y-%m-%d %H:%M:%S')
        if item_date >= yesterday and int(item['date_round']) not in existing_rounds:
            new_rows.append([
                item['reg_date'],
                int(item['date_round']),
                item['start_point'],
                int(item['line_count']),
                item['odd_even']
            ])
    except Exception as e:
        print(f"⚠ 필터링 중 오류 발생: {e}")

# === 시트에 저장 ===
if new_rows:
    worksheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"✅ 저장된 회차: {[row[1] for row in new_rows]}")
else:
    print("⚠ 저장할 신규 회차 없음")
