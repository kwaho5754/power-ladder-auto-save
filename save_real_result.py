import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 환경변수에서 서비스 계정 JSON 불러오기
json_content = os.environ.get("GOOGLE_SHEET_JSON")
if not json_content:
    raise Exception("환경변수 GOOGLE_SHEET_JSON이 설정되지 않았습니다.")

# JSON을 로컬에 저장
with open("service_account.json", "w") as f:
    f.write(json_content)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = sheet.worksheet("예측결과")

# 실시간 결과 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
if response.status_code != 200:
    raise Exception("실시간 결과 데이터를 불러오는 데 실패했습니다.")

data = response.json()

# 데이터 정리
reg_date = data['reg_date']
round_num = data['date_round']
start_point = data['start_point']
line_count = data['line_count']
odd_even = data['odd_even']
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

row = [timestamp, reg_date, round_num, start_point, line_count, odd_even]

# 시트에 중복 확인 후 추가
existing_data = worksheet.get_all_values()
existing_rows = [r[2] for r in existing_data[1:] if len(r) > 2]

if str(round_num) not in existing_rows:
    worksheet.append_row(row)
    print("✅ 저장 완료:", row)
else:
    print("⚠️ 이미 저장된 회차:", round_num)
