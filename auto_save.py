import requests
import gspread
import json
import os
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 현재 시간 출력
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"[🟢 Now] - 실시간 결과 저장 중... ({now})")

# ✅ JSON 환경변수 불러오기 및 credentials 설정
google_json = os.environ.get("GOOGLE_SHEET_JSON")
if not google_json:
    print("❌ 환경변수 'GOOGLE_SHEET_JSON' 없음")
    exit()

google_dict = json.loads(google_json)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_dict, scope)
gc = gspread.authorize(credentials)

# ✅ 구글 시트 열기
spreadsheet = gc.open("실시간결과")  # 시트 이름 확인
worksheet = spreadsheet.worksheet("예측결과")  # 시트 탭 이름도 동일하게 설정해야 함

# ✅ 실시간 결과 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
try:
    response = requests.get(url)
    data = response.json()
    latest = data[0]  # 가장 최근 항목

    # ✅ 회차 번호 조정 (현재 회차가 진행 중이므로 -1 해야 직전 완료된 회차가 됨)
    round_number = int(latest["date_round"]) - 1

    row = [
        latest["reg_date"],       # 날짜
        round_number,             # 회차
        latest["start_point"],    # 좌/우
        latest["line_count"],     # 줄 수 (3/4)
        latest["odd_even"]        # 홀/짝
    ]

    # ✅ 중복 저장 방지: 시트에 이미 저장된 마지막 회차 확인
    last_row = worksheet.get_all_values()[-1]
    last_round = int(last_row[1]) if len(last_row) >= 2 else 0

    if round_number > last_round:
        worksheet.append_row(row)
        print(f"[✅ 수집 완료] {latest['reg_date']} - {round_number}회차")
    else:
        print(f"[⚠️ 이미 저장됨] {round_number}회차")

except Exception as e:
    print(f"[❌ 오류] 실시간 결과 저장 실패: {e}")
