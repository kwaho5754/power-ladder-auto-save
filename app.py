import os
import json
import requests
from flask import Flask
import gspread
from google.oauth2.service_account import Credentials

# 환경변수에서 JSON 문자열을 받아 파일로 저장
credentials_json = os.getenv("GOOGLE_SHEET_JSON")
with open("google_sheet_credentials.json", "w") as f:
    f.write(credentials_json)

# Google Sheets 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("google_sheet_credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# 스프레드시트 및 시트 선택
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
sheet_name = "예측결과"
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# Flask 앱 설정
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Power Ladder Auto Save is running!'

@app.route('/save_recent_result', methods=['GET'])
def save_recent_result():
    # 최근 결과 JSON 가져오기
    url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
    response = requests.get(url)
    if response.status_code != 200:
        return '❌ Failed to fetch recent result', 500

    data = response.json()

    round_number = str(data['round'])   # 회차
    game_time = data['time']            # 시간
    results = data['result']            # 결과 (예: ['짝', '홀', '좌', '4'])

    # 시트에서 마지막 50개 회차 조회
    existing_data = sheet.get_all_values()
    existing_rounds = [row[0] for row in existing_data]

    # 중복 저장 방지
    if round_number in existing_rounds:
        return f'🔁 Already saved round {round_number}', 200

    # 새 데이터 추가
    new_row = [round_number, game_time] + results
    sheet.append_row(new_row)
    return f'✅ Saved round {round_number}', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
