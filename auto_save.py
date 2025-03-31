import requests
import gspread
import json
from datetime import datetime
from google.oauth2.service_account import Credentials
import os

print("✅ [Now] - 실시간 결과 저장 중...")

# ✅ 서비스 계정 JSON을 환경 변수에서 가져오기
json_str = os.environ.get('GOOGLE_SHEET_JSON')
service_account_info = json.loads(json_str)

# ✅ 구글 시트 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
gc = gspread.authorize(credentials)

# ✅ 시트 열기
spreadsheet = gc.open("실시간결과")
worksheet = spreadsheet.sheet1  # '시트1'을 기본 사용

# ✅ 실시간 결과 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, list) and len(data) > 0:
        latest = data[-1]
        reg_date = latest["reg_date"]
        round_number = latest["date_round"]
        start_point = latest["start_point"]
        line_count = latest["line_count"]
        odd_even = latest["odd_even"]

        print(f"📥 수집 성공: {round_number}회차")

        # ✅ 시트에 추가
        worksheet.append_row([reg_date, round_number, start_point, line_count, odd_even])
        print(f"📗 Google Sheets 저장 완료: {round_number}회차")
    else:
        print("❌ JSON 데이터가 비어 있습니다.")

except Exception as e:
    print(f"❌ 수집 실패: {e}")
