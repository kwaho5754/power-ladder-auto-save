import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. 구글 API 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
client = gspread.authorize(creds)

# 2. 시트 열기
spreadsheet_id = "YOUR_SPREADSHEET_ID"  # 구글 스프레드시트 ID
worksheet = client.open_by_key(spreadsheet_id).worksheet("예측결과")  # 시트 이름

# 3. 데이터 가져오기
data = worksheet.get_all_records()  # 시트에서 모든 데이터 가져오기

# 4. 마지막 데이터 추출
latest = data[-1]  # 마지막 데이터 가져오기

# 5. 데이터 저장
row = [
    latest["reg_date"],    # 'reg_date' 필드
    latest["date_round"],  # 'date_round' 필드
    latest["start_point"], # 'start_point' 필드
    latest["line_count"],  # 'line_count' 필드
    latest["odd_even"]     # 'odd_even' 필드
]

# 6. 중복 회차 저장 방지
existing = worksheet.col_values(2)  # 회차를 기준으로 중복 확인 (2번째 컬럼)
if str(latest["date_round"]) not in existing:
    worksheet.append_row(row)  # 중복이 없으면 시트에 추가
    print("✅ 저장 완료:", row)
else:
    print(f"⚠️ 이미 저장된 회차입니다: {latest['date_round']}")

