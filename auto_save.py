import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 환경 변수에서 서비스 계정 JSON 파일 경로 읽어오기
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")

# 환경변수 값 확인
print("환경변수 값:", service_account_json)

# 2. 환경변수에서 경로가 없다면 예외 처리
if not service_account_json:
    raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")

# 3. 구글 API 인증을 위한 범위 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 4. 인증 진행
credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_json, scope)
client = gspread.authorize(credentials)

# 5. 스프레드시트 ID (이 부분은 직접 입력하거나 환경변수에서 읽을 수 있음)
spreadsheet_id = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'

# 6. 구글 시트 열기
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")  # 시트 이름을 수정해주세요

# 7. 예시: 시트에서 데이터 읽기
data = worksheet.get_all_records()
print("데이터 읽기 완료:", data)

# 8. 예시: 데이터 추가하기
row = ["2025-04-06", "238", "LEFT", "3", "EVEN"]
worksheet.append_row(row)
print("데이터 저장 완료:", row)
