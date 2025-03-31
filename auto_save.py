import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# ✅ [1] 현재 시간 출력
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[🟢 Now] - 실시간 결과 저장 중... ({now})")

# ✅ [2] 구글 시트 인증 처리
json_str = os.environ.get('GOOGLE_SHEET_JSON')
info = json.loads(json_str)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
gc = gspread.authorize(credentials)

# ✅ [3] 시트 열기 및 현재 저장된 마지막 회차 확인
spreadsheet = gc.open("실시간결과")   # 📌 시트 제목 정확히 입력
worksheet = spreadsheet.sheet1
existing_data = worksheet.get_all_values()
existing_rounds = [int(row[1]) for row in existing_data[1:] if row[1].isdigit()]
last_saved_round = max(existing_rounds) if existing_rounds else 0

# ✅ [4] 실시간 결과 2개 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# ✅ [5] 회차 순으로 정렬하여 새로운 회차만 저장
new_rows = []
for item in sorted(data, key=lambda x: x["date_round"]):
    round_number = int(item["date_round"])
    if round_number > last_saved_round:
        reg_date = item["reg_date"]
        start_point = item["start_point"]
        line_count = item["line_count"]
        odd_even = item["odd_even"]
        new_rows.append([reg_date, round_number, start_point, line_count, odd_even])

# ✅ [6] 시트에 저장
if new_rows:
    worksheet.append_rows(new_rows)
    for row in new_rows:
        print(f"[✅ 수집 완료] {row[0]} - {row[1]}회차")
else:
    print(f"[⚠️ 이미 저장됨] {last_saved_round}회차")
