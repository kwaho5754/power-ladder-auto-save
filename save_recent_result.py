import requests
import gspread
from google.oauth2.service_account import Credentials

# 🟡 환경변수로 불러온 JSON을 credentials.json으로 저장했을 경우
SERVICE_ACCOUNT_FILE = "credentials.json"  
SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"

# 구글 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

# 시트에 저장된 기존 회차 가져오기
existing_rounds = sheet.col_values(1)[1:]  # 첫 번째 열, 헤더 제외

# 🔵 JSON 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

# 데이터 파싱
results = data.get("rows", [])

# 새로운 회차만 저장
new_rows = []
for item in results:
    round_number = str(item["round"])
    if round_number not in existing_rounds:
        new_rows.append([
            round_number,
            item["time"],
            item["ladder_1"],
            item["ladder_2"],
            item["ladder_3"],
            item["ladder_4"],
            item["result"]
        ])

# 시트에 추가 저장
if new_rows:
    sheet.append_rows(new_rows)
    print(f"{len(new_rows)}개 회차 저장 완료")
else:
    print("저장할 새로운 회차가 없습니다.")
