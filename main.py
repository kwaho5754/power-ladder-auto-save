import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 인증 범위 설정
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

# credentials.json 경로 설정
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

# Google Sheets API 클라이언트 설정
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open("실시간결과").sheet1  # "Your Google Sheet Name"을 실제 시트 이름으로 변경

# 데이터 읽기
data = sheet.get_all_records()

# 새로운 데이터 추가
sheet.append_row(["New", "Data", "Here"])

# 데이터 출력
print(data)
