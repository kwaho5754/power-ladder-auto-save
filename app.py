from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json

app = Flask(__name__)

# 🔐 Render용: 환경변수에서 서비스 계정 JSON 받아오기
google_sheet_json = os.environ.get("GOOGLE_SHEET_JSON")
with open("temp_credentials.json", "w") as f:
    f.write(google_sheet_json)

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
creds = ServiceAccountCredentials.from_json_keyfile_name('temp_credentials.json', scope)
gs = gspread.authorize(creds)

# 📗 시트 정보 설정
SPREADSHEET_KEY = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet('예측결과')

# 🧠 현재 회차 계산 함수
def get_current_round():
    now = datetime.now()
    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    minutes_passed = int((now - start_time).total_seconds() // 60)
    round_number = minutes_passed // 5 + 1
    return round_number

# 🔍 실시간 JSON 결과 가져오기 (최근 회차 데이터)
def fetch_latest_result():
    url = 'https://ntry.com/data/json/games/power_ladder/recent_result.json'
    try:
        res = requests.get(url)
        res.raise_for_status()
        data = res.json()
        return {
            'round': data['round'],
            'left_right': data['left_right'],
            'odd_even': data['odd_even'],
            'start_position': data['start_position'],
            'ladder_count': data['ladder_count'],
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"❌ 실시간 데이터 수집 오류: {e}")
        return None

# ✅ 중복 저장 방지용: 시트에 이미 저장된 회차 불러오기
def get_saved_rounds():
    try:
        rounds = worksheet.col_values(1)[1:]  # 헤더 제외
        return [int(r) for r in rounds if r.isdigit()]
    except:
        return []

# 🔄 누적 저장 기능 (중복 회차 제외)
def append_new_result():
    latest = fetch_latest_result()
    if not latest:
        return '데이터 수집 실패'

    saved = get_saved_rounds()
    if int(latest['round']) in saved:
        return f"✅ 이미 저장된 회차입니다: {latest['round']}"

    row = [
        latest['round'], latest['left_right'], latest['odd_even'],
        latest['start_position'], latest['ladder_count'], latest['timestamp']
    ]
    worksheet.append_row(row)
    return f"🟢 저장 완료 - 회차: {latest['round']}"

# 📡 수동 실행용 엔드포인트
@app.route('/run-manual')
def run_manual():
    result = append_new_result()
    return jsonify({'message': result})

# ✅ 루트 확인
@app.route('/')
def home():
    return "✅ Power Ladder Auto Save Running"

if __name__ == '__main__':
    app.run(debug=True)