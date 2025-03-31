import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ✅ 실시간 회차 데이터 URL
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

try:
    response = requests.get(url)
    data = response.json()
    latest = data[-1]  # 리스트의 마지막 항목이 최신 회차

    round_number = latest["date_round"]
    reg_date = latest["reg_date"]
    start_point = latest["start_point"]
    line_count = latest["line_count"]
    odd_even = latest["odd_even"]

    print(f"🟢 수집 성공: {round_number}회차")

except Exception as e:
    print(f"🔴 데이터 수집 실패: {e}")
    exit()

# ✅ 구글 시트 인증 처리
try:
    json_str = os.environ.get("GOOGLE_SHEET_JSON")
    json_dict = json.loads(json_str)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(json_dict, scope)
    gc = gspread.authorize(credentials)

    # ✅ 시트 열기
    sh = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
    worksheet = sh.worksheet("예측결과")

    # ✅ 데이터 추가
    worksheet.append_row([
        reg_date,
        str(round_number),
        start_point,
        line_count,
        odd_even,
        "", "", "", ""  # 예측 결과(1~3위)는 비워둠
    ])

    print(f"✅ Google Sheets 저장 완료: {round_number}회차")

except Exception as e:
    print(f"🔴 시트 저장 실패: {e}")
