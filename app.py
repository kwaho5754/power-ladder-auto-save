import os
import json
import requests
from flask import Flask
import gspread
from google.oauth2.service_account import Credentials

# 🔐 환경변수에서 서비스 계정 JSON 받아와서 임시 저장
credentials_json = os.getenv("GOOGLE_SHEET_JSON")
with open("google_sheet_credentials.json", "w") as f:
    f.write(credentials_json)

# ✅ Google Sheets 인증
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("google_sheet_credentials.json", scopes=scopes)
client = gspread.authorize(creds)

# ✅ 스프레드시트 및 워크시트 설정
spreadsheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
sheet_name = "예측결과"
sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)

# ✅ Flask 앱 설정
app = Flask(__name__)

@app.route('/')
def home():
    return '✅ Power Ladder Auto Save is running!'

@app.route('/save_recent_result', methods=['GET'])
def save_recent_result():
    try:
        # 🔄 실시간 결과 API 호출
        url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
        response = requests.get(url)
        if response.status_code != 200:
            return '❌ Failed to fetch recent result', 500

        data = response.json()

        # ✅ 리스트 형태일 경우 첫 번째 요소만 사용
        if isinstance(data, list):
            if not data:
                return '❌ No data received (empty list)', 200
            data = data[0]
        elif not isinstance(data, dict):
            return '❌ Unknown data format from API', 500

        # ✅ 회차 및 결과 추출
        round_number = str(data['date_round'])  # 회차
        game_time = data['reg_date']            # 날짜
        results = [data['odd_even'], data['start_point'], data['line_count']]  # 결과

        # ✅ 시트 내 중복 회차 확인
        existing_data = sheet.get_all_values()
        existing_rounds = [row[0] for row in existing_data]

        if round_number in existing_rounds:
            return f'🔁 Already saved round {round_number}', 200

        # ✅ 새 행 추가
        new_row = [round_number, game_time] + results
        sheet.append_row(new_row)

        return f'✅ Saved round {round_number}', 200

    except Exception as e:
        return f'❌ Internal error: {str(e)}', 500

# ✅ Render 실행용 포트 설정
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
