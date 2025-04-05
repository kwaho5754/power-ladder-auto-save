import os
import json
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# 서비스 계정 JSON을 환경변수에서 불러와 임시 파일로 저장
json_content = os.environ.get("GOOGLE_SHEET_JSON")
if not json_content:
    raise Exception("환경변수 GOOGLE_SHEET_JSON이 없습니다.")

with open("service_account.json", "w") as f:
    f.write(json_content)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)

# 스프레드시트 및 시트 이름
spreadsheet = gc.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = spreadsheet.worksheet("예측결과")

# 현재 시트에서 저장된 회차 불러오기
existing_rounds = worksheet.col_values(1)[1:]  # 헤더 제외
existing_rounds = [str(r).strip() for r in existing_rounds]

# 실시간 JSON 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
res = requests.get(url)
data = res.json()

# 최신 회차 데이터만 사용
latest = data[0] if isinstance(data, list) and len(data) > 0 else None
if not latest:
    print("⚠️ 최신 데이터가 없습니다.")
    exit()

# 필요한 정보 추출
round_number = str(latest["date_round"])
if round_number in existing_rounds:
    print(f"✅ 이미 저장된 회차: {round_number}")
    exit()

reg_date = latest["reg_date"]
start_point = latest["start_point"]
line_count = latest["line_count"]
odd_even = latest["odd_even"]

# 시트에 추가
worksheet.append_row([round_number, reg_date, start_point, line_count, odd_even])
print(f"✅ Round {round_number} 저장 완료!")
