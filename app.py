from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta
import os
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Google Sheets 연동 설정
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_str = os.environ.get("GOOGLE_SHEET_JSON")
    if not json_str:
        raise Exception("환경변수 'GOOGLE_SHEET_JSON' 설정 필요")
    info = json.loads(json_str)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4").worksheet("예측결과")
    return sheet

# 실시간 회차 데이터 수집 API
@app.route("/run-manual", methods=["GET"])
def run_manual():
    url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
    res = requests.get(url)
    data = res.json()

    def format_comb(result):
        return f"{result['p_left']}{result['p_ladder']}-{result['p_right']}{result['p_odd_even']}"

    def parse_time(timestr):
        return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")

    # 최근 24시간 내 데이터 필터링
    now = datetime.now()
    valid_data = [d for d in data if now - parse_time(d['game_date']) <= timedelta(hours=24)]

    # 시트 불러오기
    try:
        sheet = get_sheet()
        existing_rounds = set(row[1] for row in sheet.get_all_values()[1:])  # 1열: 날짜, 2열: 회차
    except Exception as e:
        return jsonify({"error": str(e)})

    saved = 0
    for d in valid_data:
        round_key = d['game_round']
        if round_key not in existing_rounds:
            row = [d['game_date'], round_key, format_comb(d)]
            sheet.append_row(row)
            saved += 1

    # 분석 - 조합 빈도수 기반 예측
    all_data = sheet.get_all_values()[1:]  # 헤더 제외
    comb_counter = {}
    for row in all_data:
        comb = row[2]
        comb_counter[comb] = comb_counter.get(comb, 0) + 1

    sorted_comb = sorted(comb_counter.items(), key=lambda x: x[1], reverse=True)
    top3 = [item[0] for item in sorted_comb[:3]]

    return jsonify({
        "총 분석 데이터 수": len(all_data),
        "상위 3개 조합": top3,
        "방금 저장된 회차 수": saved
    })

# 루트 주소는 확인용
@app.route("/")
def index():
    return "Power Ladder Prediction API"

if __name__ == "__main__":
    app.run(debug=True)