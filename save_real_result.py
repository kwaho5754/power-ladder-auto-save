import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets 인증을 위한 환경변수에서 서비스 계정 불러오기
json_content = os.environ.get("GOOGLE_SHEET_JSON")
if not json_content:
    raise Exception("환경변수 GOOGLE_SHEET_JSON이 없습니다.")

# JSON을 로컬 파일로 저장
with open("service_account.json", "w") as f:
    f.write(json_content)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 시트 연결
sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = sheet.worksheet("예측결과")

# 실시간 결과 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# 결과값 파싱
reg_date = data['reg_date']                      # 날짜 (예: 2025-03-31)
round_num = str(data['date_round'])              # 회차 (예: 119)
start_point = data['start_point']                # LEFT / RIGHT
line_count = data['line_count']                  # 3 or 4
odd_even = data['odd_even']                      # EVEN / ODD
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 저장 시간

# 시트 중복 확인 후 저장
existing_rows = worksheet.get_all_values()
saved_rounds = [row[2] for row in existing_rows[1:] if len(row) > 2]  # 3번째 열이 회차 번호

if round_num not in saved_rounds:
    new_row = [timestamp, reg_date, round_num, start_point, line_count, odd_even]
    worksheet.append_row(new_row)
    print("✅ 저장 완료:", new_row)
else:
    print("⛔ 이미 저장된 회차:", round_num)
