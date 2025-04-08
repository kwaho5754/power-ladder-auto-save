import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ✅ 1. 환경변수에서 서비스 계정 정보 로딩
json_str = os.environ.get('GOOGLE_SHEET_JSON')
if not json_str:
    raise ValueError("환경변수 'GOOGLE_SHEET_JSON'이 설정되지 않았습니다.")
service_account_info = json.loads(json_str)

# ✅ 2. 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(credentials)

# ✅ 3. 구글 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")

# ✅ 4. 시트에서 기존 회차 읽기
existing_rounds = worksheet.col_values(2)[1:]  # 두 번째 열(date_round) 기준, 헤더 제외
existing_rounds = set(existing_rounds)

# ✅ 5. 실시간 JSON 데이터 요청
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
result = response.json()["list"][:2]  # 최근 2개만

# ✅ 6. 새 데이터 중 시트에 없는 회차만 저장
for data in result:
    round_number = str(data["date_round"])
    if round_number not in existing_rounds:
        row = [
            data["reg_date"],
            data["date_round"],
            data["start_point"],
            data["line_count"],
            data["odd_even"]
        ]
        worksheet.append_row(row)
        print("✅ 시트에 데이터가 저장되었습니다:", row)
    else:
        print("⏭ 이미 저장된 회차입니다:", round_number)
