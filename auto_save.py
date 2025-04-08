import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 환경변수에서 서비스 계정 JSON 문자열 가져오기
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
if not service_account_json:
    raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

# 🔑 JSON 문자열을 파싱하여 자격 증명 생성
info = json.loads(service_account_json)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
client = gspread.authorize(credentials)

# 📄 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")

# 📦 외부 JSON 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
result = response.json()

# 📌 가장 최근 데이터 추출
latest = result[0]  # <-- 수정된 부분: 리스트이므로 인덱스로 접근

# 🔁 중복 방지: 시트에 같은 회차가 이미 있는지 확인
existing_rounds = worksheet.col_values(2)  # 'date_round' 열
if str(latest["date_round"]) not in existing_rounds:
    row = [
        latest["reg_date"],
        latest["date_round"],
        latest["start_point"],
        latest["line_count"],
        latest["odd_even"]
    ]
    worksheet.append_row(row)
    print("✅ 시트에 데이터가 저장되었습니다.")
else:
    print("⚠️ 이미 존재하는 회차입니다. 저장하지 않습니다.")
