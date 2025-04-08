import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 환경변수에서 서비스 계정 키 불러오기
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
if not service_account_json:
    raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

# JSON 문자열을 딕셔너리로 변환
service_account_info = json.loads(service_account_json)

# ✅ 구글 시트 API 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(credentials)

# ✅ 구글 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = gc.open_by_key(spreadsheet_id).worksheet("예측결과")

# ✅ 최신 JSON 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
result = response.json()
latest = result["list"][0]  # 최신 데이터

# ✅ 시트에 이미 있는지 확인 후 저장
reg_date = latest["reg_date"]
date_round = latest["date_round"]

existing = worksheet.get_all_values()
if [reg_date, str(date_round)] not in [[row[0], row[1]] for row in existing]:
    new_row = [
        reg_date,
        date_round,
        latest["start_point"],
        latest["line_count"],
        latest["odd_even"]
    ]
    worksheet.append_row(new_row)
    print("✅ 시트에 데이터가 저장되었습니다.")
else:
    print("⏩ 이미 저장된 회차입니다. 저장하지 않음.")
