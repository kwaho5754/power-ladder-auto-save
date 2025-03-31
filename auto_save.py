import json
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 현재 시간 출력
now = datetime.now()
print(f"[🕒 Now] - 실시간 결과 저장 중... ({now.strftime('%Y-%m-%d %H:%M:%S')})")

# ✅ 실시간 회차 정보 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

try:
    response = requests.get(url)
    data = response.json()

    # 마지막 항목 = 가장 최근 회차
    latest_result = data[-1]
    reg_date = latest_result["reg_date"]
    date_round = latest_result["date_round"]
    start_point = latest_result["start_point"]
    line_count = latest_result["line_count"]
    odd_even = latest_result["odd_even"]

    print(f"[✅ 수집 완료] {reg_date} - {date_round}회차")

except Exception as e:
    print(f"[❌ 오류] 실시간 데이터 수집 실패 - {e}")
    exit()

# ✅ 구글 시트 인증 및 저장
try:
    # Render에서는 환경변수로 JSON이 저장되어 있음
    import os
    service_account_json = os.environ.get("GOOGLE_SHEET_JSON")
    if not service_account_json:
        raise Exception("GOOGLE_SHEET_JSON 환경변수가 설정되지 않았습니다.")

    # 환경변수 JSON 문자열을 임시 파일로 저장
    with open("service_account.json", "w") as f:
        f.write(service_account_json)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    gc = gspread.authorize(credentials)

    # ✅ 시트 열기 (시트 이름: 예측결과)
    spreadsheet = gc.open("예측결과")
    worksheet = spreadsheet.sheet1  # 첫 번째 시트 사용

    # ✅ 새 행 추가
    new_row = [reg_date, date_round, start_point, line_count, odd_even]
    worksheet.append_row(new_row)

    print(f"[📥 Google Sheets] 저장 완료: {date_round}회차")

except Exception as e:
    print(f"[❌ Google Sheets 저장 실패] - {e}")
