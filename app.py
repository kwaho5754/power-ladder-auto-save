from flask import Flask, jsonify
from datetime import datetime, timedelta
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# 구글 시트 설정
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('google_sheet_credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open_by_key('1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4').worksheet('예측결과')

def get_current_round():
    now = datetime.now()
    return now.hour * 12 + now.minute // 5 + 1

def get_today_date():
    return datetime.now().strftime('%Y-%m-%d')

def get_existing_rounds():
    records = sheet.get_all_records()
    return {(r['game_date'], int(r['round'])) for r in records if 'game_date' in r and 'round' in r}

def fetch_current_result():
    try:
        res = requests.get("https://ntry.com/data/json/games/power_ladder/recent_result.json")
        data = res.json()
        return {
            'game_date': get_today_date(),
            'round': int(data['round']),
            'result': data['result']  # 추가 필드
        }
    except Exception as e:
        print("🔴 데이터 가져오기 실패:", e)
        return None

def save_to_sheet(entry):
    try:
        sheet.append_row([entry['game_date'], entry['round'], entry['result']])
        print(f"✅ 저장 완료: {entry['game_date']} {entry['round']}회차")
    except Exception as e:
        print("❌ 저장 실패:", e)

@app.route('/')
def index():
    return '✅ 서버 정상 작동 중!'

@app.route('/run-manual')
def run_manual():
    entry = fetch_current_result()
    if not entry:
        return jsonify({'status': 'fail', 'message': '데이터 수집 실패'})

    existing = get_existing_rounds()
    key = (entry['game_date'], entry['round'])
    if key not in existing:
        save_to_sheet(entry)
        return jsonify({'status': 'saved', 'data': entry})
    else:
        print("⚠️ 이미 저장된 회차입니다.")
        return jsonify({'status': 'exists', 'data': entry})

if __name__ == '__main__':
    app.run(debug=True)
