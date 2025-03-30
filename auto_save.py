import requests
import gspread
from google.oauth2.service_account import Credentials

# 구글 인증 정보
SERVICE_ACCOUNT_FILE = 'sheet-access.json'
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
WORKSHEET_NAME = '시트1'

# 구글 시트 인증
scopes = ['https://www.googleapis.com/auth/spreadsheets']
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(credentials)
worksheet = gc.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME)

# 실시간 데이터 가져오기
url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
response = requests.get(url)
data = response.json()[0]  # 최신 회차 1개

# 필요한 값 추출
reg_date = data["reg_date"]
round_num = data["date_round"]
start = data["start_point"]
line = data["line_count"]
odd_even = data["odd_even"]

# 시트에 추가
new_row = [reg_date, round_num, start, line, odd_even]
worksheet.append_row(new_row)
print("✅ 저장 완료:", new_row)
