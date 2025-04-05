from flask import Flask
import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return '✅ Power Ladder Auto Save is running!'

@app.route('/save_recent_result')
def save_recent_result():
    try:
        # ▶️ 1. 실시간 결과 JSON 주소 요청
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()

        # ⚠️ 리스트가 비어있으면 예외 처리
        if not isinstance(data, list) or len(data) == 0:
            return "⚠️ No recent result data available.", 500

        # ▶️ 2. 가장 최신 회차 데이터 추출
        latest = data[0]
        round_number = str(latest.get('date_round', ''))
        reg_date = latest.get('reg_date', '')
        start_point = latest.get('start_point', '')
        line_count = latest.get('line_count', '')
        odd_even = latest.get('odd_even', '')

        # ▶️ 3. 구글 시트 인증 (환경변수에서 불러와 파일로 저장)
        json_str = os.environ.get('GOOGLE_SHEET_JSON')
        if not json_str:
            return "⚠️ GOOGLE_SHEET_JSON env variable not found", 500

        json_path = '/tmp/credential.json'
        with open(json_path, 'w') as f:
            f.write(json_str)

        # ▶️ 4. Google Sheets API 연결
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
        gc = gspread.authorize(credentials)

        # ▶️ 5. 구글 시트 열기 및 시트 선택
        sheet_id = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'  # 실시간결과 문서 ID
        sheet = gc.open_by_key(sheet_id).worksheet('예측결과')

        # ▶️ 6. 중복 확인: 이미 있는 회차인지 확인
        existing = sheet.col_values(1)
        if round_number in existing:
            return f"⚠️ Round {round_number} already exists.", 200

        # ▶️ 7. 시트에 새 데이터 추가
        sheet.append_row([round_number, reg_date, start_point, line_count, odd_even])
        return f"✅ Round {round_number} saved successfully!", 200

    except Exception as e:
        return f"❌ Internal error: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)
