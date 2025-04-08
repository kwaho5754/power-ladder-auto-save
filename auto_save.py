import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ▶ 환경변수에서 서비스 계정 JSON 가져오기
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
if service_account_json is None:
    raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

# ▶ JSON 문자열을 딕셔너리로 변환
service_account_info = json.loads(service_account_json)

# ▶ 인증 및 시트 열기
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# ▶ Google Sheets ID와 워크시트 이름
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(spreadsheet_id).worksheet("예측결과")

# ▶ 최신 데이터 불러오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
result = response.json()

# ▶ result는 리스트 형태로 감싸져 있다고 가정
latest = result[0]

# ▶ 저장할 값 추출
reg_date = latest["reg_date"]
date_round = latest["date_round"]
start_point = latest["start_point"]
line_count = latest["line_count"]
odd_even = latest["odd_even"]

# ▶ 중복 체크
existing_data = worksheet.get_all_values()
if [str(reg_date), str(date_round), start_point, str(line_count), odd_even] in existing_data:
    print("✅ 이미 저장된 데이터입니다.")
else:
    worksheet.append_row([reg_date, date_round, start_point, line_count, odd_even])
    print("✅ 시트에 데이터가 저장되었습니다.")
