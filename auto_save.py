import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 인증 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(credentials)

# 구글 시트 ID와 시트 이름 설정
spreadsheet_id = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'  # 구글 시트 ID
worksheet_name = '예측결과'  # 구글 시트 이름

# 구글 시트 열기
worksheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)

# 데이터를 가져오고 처리하는 코드
data = [
    {"reg_date": "2025-04-06", "date_round": 238, "start_point": "LEFT", "line_count": 3, "odd_even": "EVEN"},
    {"reg_date": "2025-04-06", "date_round": 239, "start_point": "RIGHT", "line_count": 4, "odd_even": "ODD"},
    # 추가 데이터...
]

# 데이터를 시트에 입력
for row in data:
    # 예시로 하나씩 삽입
    worksheet.append_row([row["reg_date"], row["date_round"], row["start_point"], row["line_count"], row["odd_even"]])

print("데이터가 성공적으로 시트에 저장되었습니다.")
