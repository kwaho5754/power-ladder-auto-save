from datetime import datetime, timedelta
import requests
import json
from flask import Flask, jsonify
from google.oauth2.service_account import Credentials
import gspread

app = Flask(__name__)

# 구글 시트 인증
SHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
creds = Credentials.from_service_account_file(
    "google_sheet_credentials.json",
    scopes=["https://www.googleapis.com/auth/spreadsheets"]
)
gc = gspread.authorize(creds)
worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# ✅ 현재 회차 가져오기
def get_current_round():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        response.encoding = "utf-8-sig"
        data = response.json()

        # 현재 한국 시간 기준 날짜
        now = datetime.utcnow() + timedelta(hours=9)
        midnight = datetime(now.year, now.month, now.day)
        first_game_time = midnight
        game_interval = timedelta(minutes=5)

        latest_round = int(data[0]["round"])
        latest_time_str = data[0]["date"] + " " + data[0]["time"]
        latest_time = datetime.strptime(latest_time_str, "%Y-%m-%d %H:%M:%S")

        elapsed = latest_time - first_game_time
        round_num = int(elapsed.total_seconds() // 300) + 1
        return round_num
    except Exception as e:
        print("⚠️ 회차 계산 오류:", e)
        return None

# ✅ 수동 실행 API
@app.route("/run-manual", methods=["GET"])
def run_manual():
    current_round = get_current_round()
    if not current_round:
        return jsonify({"message": "현재 회차를 가져오지 못했습니다."})

    # 시트에서 이미 저장된 회차 불러오기
    existing_data = worksheet.get_all_values()
    existing_rounds = [row[0] for row in existing_data[1:] if row]

    if str(current_round) in existing_rounds:
        return jsonify({"message": f"{current_round}회차는 이미 저장되어 있습니다."})

    # 저장할 예시 데이터 (예측 로직 연동 필요)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    example_data = [str(current_round), now, "좌삼짧", "우삼홀", "좌사홀", "우사짧", "1위", "2위", "3위"]
    worksheet.append_row(example_data)

    return jsonify({"message": f"{current_round}회차 저장 완료"})

# 기본 루트
@app.route("/", methods=["GET"])
def home():
    return "✅ Power Ladder Auto Save is running!"

if __name__ == "__main__":
    app.run(debug=True)
