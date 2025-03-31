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

# === 기존 저장 회차 목록 불러오기 ===
existing_rounds_raw = worksheet.col_values(2)[1:]  # B열
existing_rounds = []
for r in existing_rounds_raw:
    try:
        existing_rounds.append(int(r))
    except ValueError:
        continue

# === 24시간 전 계산 ===
now = datetime.now(pytz.timezone("Asia/Seoul"))
yesterday = now - timedelta(days=1)

# === 실시간 결과 불러오기 ===
url = "https://ntry.com/data/json/games/power_ladder/result.json"
response = requests.get(url)
data = response.json()

# ✅ 내부 result 키가 있는지 확인
if isinstance(data, dict) and "result" in data:
    data = data["result"]

# === 24시간 내 필터링 및 저장할 데이터 ===
new_rows = []
for item in data:
    try:
        reg_time = datetime.strptime(item['reg_date'], '%Y-%m-%d %H:%M:%S')
        round_num = int(item['date_round'])

        if reg_time >= yesterday and round_num not in existing_rounds:
            new_rows.append([
                item['reg_date'],
                round_num,
                item['start_point'],
                int(item['line_count']),
                item['odd_even']
            ])
    except Exception as e:
        print(f"⚠️ 필터링 중 오류 발생: {e}")

# === 시트에 저장 ===
if new_rows:
    worksheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"✅ 저장된 회차: {[row[1] for row in new_rows]}")
else:
    print("⚠️ 저장할 신규 회차 없음")
