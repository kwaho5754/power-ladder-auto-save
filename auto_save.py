import os
import json
import gspread
from google.oauth2.service_account import Credentials

# 1. 환경변수에서 JSON 문자열 가져오기
json_str = os.environ.get("GOOGLE_SHEET_JSON")

if not json_str:
    raise ValueError("환경변수 'GOOGLE_SHEET_JSON'이 설정되지 않았습니다.")

# 2. JSON 문자열을 실제 파일로 저장
json_path = "service_account.json"
with open(json_path, "w") as f:
    f.write(json_str)

# 3. 서비스 계정 인증
credentials = Credentials.from_service_account_file(
    json_path,
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# 4. gspread 클라이언트 인증
client = gspread.authorize(credentials)

# 5. 스프레드시트 연결
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")

# 6. 저장할 데이터 예시
data = {
    "reg_date": "2025-04-06",
    "date_round": 238,
    "start_point": "LEFT",
    "line_count": 3,
    "odd_even": "EVEN"
}

# 7. 데이터 저장
worksheet.append_row([
    data["reg_date"], data["date_round"],
    data["start_point"], data["line_count"],
    data["odd_even"]
])

print("✅ 시트에 데이터가 저장되었습니다.")
