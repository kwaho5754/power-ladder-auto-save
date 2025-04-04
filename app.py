import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# 📌 구글 시트 설정
sheet_id = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
sheet_name = "예측결과"

# 📌 서비스 계정 환경 변수에서 JSON 불러오기
json_data = os.environ.get("GOOGLE_SHEET_JSON")
if json_data is None:
    raise ValueError("환경 변수 'GOOGLE_SHEET_JSON'이 설정되지 않았습니다.")

info = json.loads(json_data)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)

# 📌 현재 회차 정보 가져오기 (ntry JSON)
def get_latest_round_info():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    res = requests.get(url)
    if res.status_code != 200:
        raise ValueError("❌ 회차 데이터를 가져올 수 없습니다.")
    data = res.json()
    return {
        "round": data[0]['round'],
        "time": data[0]['time']
    }

# ✅ 수동 실행 API → 실시간 회차 저장
@app.route("/run-manual", methods=["GET"])
def run_manual():
    try:
        sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
        existing_data = sheet.get_all_records()

        # ⏰ 현재 회차
        latest = get_latest_round_info()
        current_round = latest['round']
        current_time = latest['time']

        # ✅ 중복 방지
        existing_rounds = [str(row.get('round')) for row in existing_data]
        if str(current_round) in existing_rounds:
            return jsonify({"message": "이미 처리된 회차입니다."})

        # ✅ 시트에 저장 (빈 항목 포함)
        sheet.append_row([
            current_round,
            current_time,
            "", "", "", "", "", "", "", "", "", "", ""
        ])

        return jsonify({"message": "신규 회차 저장 완료"})

    except Exception as e:
        print(f"❌ 실시간 데이터 수집 오류: {e}")
        return jsonify({"message": f"실패: {e}"})


if __name__ == "__main__":
    app.run(debug=True)