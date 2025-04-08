import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os

# 환경변수에서 서비스 계정 정보 불러오기
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
if service_account_json is None:
    raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

# JSON 문자열을 딕셔너리로 파싱
info = json.loads(service_account_json)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
gc = gspread.authorize(credentials)

# 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(spreadsheet_id).worksheet("예측결과")

# 실시간 JSON 데이터 수집
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
result = response.json()

# 파싱
latest = result["list"][0]
reg_date = latest["reg_date"]
round_num = latest["date_round"]
start_point = latest["start_point"]
line_count = latest["line_count"]
odd_even = latest["odd_even"]

# 시트에 이미 동일한 회차가 있는지 확인
existing_data = worksheet.get_all_values()
is_duplicate = False
for row in existing_data:
    if str(round_num) in row and reg_date in row:
        is_duplicate = True
        break

# 중복이 아니면 저장
if not is_duplicate:
    worksheet.append_row([reg_date, round_num, start_point, line_count, odd_even])
    print(f"✅ 저장 완료: {[reg_date, round_num, start_point, line_count, odd_even]}")
else:
    print(f"⚠️ 이미 저장된 회차입니다: {round_num}")
