import requests
import json
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# ✅ 현재 날짜 출력
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
print(f"[🟢 Now] - 실제 결과 수집 중... ({now})")

# ✅ 실제 결과 JSON 주소
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"

try:
    response = requests.get(url)
    data = response.json()[0]  # 가장 최근 회차 결과
    reg_date = data["reg_date"]
    round_number = data["date_round"]
    start_point = data["start_point"]
    line_count = data["line_count"]
    odd_even = data["odd_even"]

    print(f"[✅ 수집 성공] {reg_date} | {round_number} | {start_point} | {line_count} | {odd_even}")

except Exception as e:
    print(f"[❌ 오류] 결과 수집 실패: {e}")
    exit()

# ✅ 구글 시트 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_str = os.environ.get("GOOGLE_SHEET_JSON")

if not json_str:
    print("[❌ 오류] GOOGLE_SHEET_JSON 환경변수가 설정되지 않았습니다.")
    exit()

info = json.loads(json_str)
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
gc = gspread.authorize(credentials)

# ✅ 시트 열기 (예측결과 시트에 저장)
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(spreadsheet_id).worksheet("예측결과")

# ✅ 시트에 행 추가
try:
    worksheet.append_row([reg_date, round_number, start_point, line_count, odd_even])
    print("[✅ 저장 완료] 시트에 결과 추가 완료")
except Exception as e:
    print(f"[❌ 저장 실패] 시트 저장 중 오류: {e}")
