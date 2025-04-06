import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
import requests

# 1. 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = os.environ.get("GOOGLE_SHEET_JSON")

with open("service_account.json", "w") as f:
    f.write(json_data)

creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 2. 시트 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
sheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")

# 3. JSON 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()  # 딕셔너리 형식

# 4. 한 줄로 저장할 데이터 구성
row = [
    data["reg_date"],
    data["date_round"],
    data["start_point"],
    data["line_count"],
    data["odd_even"]
]

# 5. 중복 체크 후 저장
existing = sheet.col_values(2)  # 회차 (B열)

if str(data["date_round"]) not in existing:
    sheet.append_row(row)
    print("✅ 저장 완료:", row)
else:
    print("⚠️ 이미 저장된 회차입니다:", data["date_round"])
