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

# ▶ 기존 시트에 있는 회차들 추출 (날짜+회차 조합으로 중복 확인)
existing_data = worksheet.get_all_values()
existing_keys = {f"{row[0]}_{row[1]}" for row in existing_data if len(row) >= 2}

# ▶ 최근 3회차 확인
for item in result[:3]:
    reg_date = item["reg_date"]
    date_round = item["date_round"]
    start_point = item["start_point"]
    line_count = item["line_count"]
    odd_even = item["odd_even"]
    
    unique_key = f"{reg_date}_{date_round}"

    if unique_key in existing_keys:
        print(f"⏩ 이미 저장된 회차입니다: {unique_key}")
        continue

    worksheet.append_row([reg_date, date_round, start_point, line_count, odd_even])
    print(f"✅ 시트에 저장됨: {reg_date}, 회차 {date_round}")
