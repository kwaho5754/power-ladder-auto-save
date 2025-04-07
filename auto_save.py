import os
import gspread
from google.oauth2.service_account import Credentials

# 환경변수에서 서비스 계정 JSON 파일 경로를 읽어오기
service_account_json = os.environ.get("GOOGLE_SHEET_JSON")

if not service_account_json:
    raise ValueError("환경변수 'GOOGLE_SHEET_JSON'이 설정되지 않았습니다.")
else:
    print("환경변수 값:", service_account_json)

# 서비스 계정 인증
credentials = Credentials.from_service_account_file(
    service_account_json, 
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)

# Google Sheets API 클라이언트 초기화
client = gspread.authorize(credentials)

# Google Sheets 문서 열기
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")

# 데이터 입력 예시 (새로운 데이터)
data = {
    "reg_date": "2025-04-06",
    "date_round": 238,
    "start_point": "LEFT",
    "line_count": 3,
    "odd_even": "EVEN"
}

# 데이터를 시트에 추가하기
worksheet.append_row([data["reg_date"], data["date_round"], data["start_point"], data["line_count"], data["odd_even"]])

print("데이터가 시트에 저장되었습니다.")
