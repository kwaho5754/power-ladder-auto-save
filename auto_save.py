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
spreadsheet = gc.open("실시간결과")  # 구글 시트 문서명
worksheet = spreadsheet.worksheet("예측결과")  # 시트 이름

# === 시트에 저장된 기존 회차 목록 불러오기 ===
existing_rounds = worksheet.col_values(2)[1:]  # B열 회차 (헤더 제외)
existing_rounds = list(map(int, existing_rounds)) if existing_rounds else []

# === 현재 시간 기준 24시간 전 계산 ===
now = datetime.now(pytz.timezone("Asia/Seoul"))
yesterday = now - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

# === 실시간 결과 JSON 불러오기 ===
url = "https://ntry.com/data/json/games/power_ladder/result.json"
response = requests.get(url)
data = response.json()

# === 날짜만 비교하는 함수 ===
def get_date_only(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime('%Y-%m-%d')
    except:
        return ""

# === 24시간 내 + 시트에 없는 회차만 필터링 ===
new_rows = []
for item in data:
    try:
        reg_date = item['reg_date']
        date_only = get_date_only(reg_date)
        round_num = int(item['date_round'])

        if date_only >= yesterday_str and round_num not in existing_rounds:
            new_rows.append([
                reg_date,
                round_num,
                item['start_point'],
                int(item['line_count']),
                item['odd_even']
            ])
    except Exception as e:
        print(f"⚠️ 필터링 중 오류 발생: {e}")

# === 시트에 결과 저장 ===
if new_rows:
    worksheet.append_rows(new_rows, value_input_option="USER_ENTERED")
    print(f"✅ 저장된 회차: {[row[1] for row in new_rows]}")
else:
    print("⚠️ 저장할 신규 회차 없음")
