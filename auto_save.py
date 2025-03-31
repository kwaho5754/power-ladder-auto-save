# auto_save.py

import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os
import json

# ✅ 현재 시간 출력
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[🕘 Now] - 실시간 결과 저장 중... ({now})")

# ✅ 실시간 JSON URL
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

try:
    response = requests.get(url)
    data = response.json()
    latest_result = data[-1]  # 마지막 항목이 가장 최근 결과

    # ✅ 데이터 추출
    reg_date = latest_result["reg_date"]
    date_round = latest_result["date_round"]
    start_point = latest_result["start_point"]
    line_count = latest_result["line_count"]
    odd_even = latest_result["odd_even"]

    print(f"[✅ 수집 완료] {reg_date} - {date_round}회차")

except Exception as e:
    print(f"[❌ 오류] 실시간 데이터 수집 실패 - {e}")
    exit()

# ✅ 구글 시트 인증
try:
    json_str = os.environ.get("GOOGLE_SHEET_JSON")
    service_account_info = json.loads(json_str)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    # ✅ 시트 열기 (시트 이름은 '예측결과')
    sheet = client.open("실시간결과").worksheet("예측결과")
    sheet.append_row([reg_date, date_round, start_point, line_count, odd_even])

    print(f"[✅ Google Sheets 저장 완료] - {date_round}회차")

except Exception as e:
    print(f"[❌ Google Sheets 저장 실패] - {e}")
