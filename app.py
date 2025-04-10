from flask import Flask, jsonify
import pandas as pd
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# 🧠 조합 이름 변환
def format_combo_name(combo):
    mapping = {
        "LEFT3ODD": "좌삼홀", "LEFT3EVEN": "좌삼짝",
        "LEFT4ODD": "좌사홀", "LEFT4EVEN": "좌사짝",
        "RIGHT3ODD": "우삼홀", "RIGHT3EVEN": "우삼짝",
        "RIGHT4ODD": "우사홀", "RIGHT4EVEN": "우사짝"
    }
    return mapping.get(combo, combo)

# 🔮 예측 함수
def predict_top3_combinations(data):
    count = Counter(data)
    top3 = [item[0] for item in count.most_common(3)]
    return top3

@app.route("/predict", methods=["GET"])
def predict():
    # 📂 구글 시트에서 CSV 가져오기
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSdr7sw0pVmKV3LUw5EAAoYo6IbMn_bOJfRP-ED9XCRPRtOPbWALiJ1dnESrxGlsQ/pub?gid=0&single=true&output=csv"
    df = pd.read_csv(sheet_url)

    # 🧹 결측치 제거
    df.dropna(subset=["결과"], inplace=True)

    # 📅 최근 5일 데이터만 사용
    df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
    recent_5days = df[df["날짜"] >= pd.Timestamp.now() - pd.Timedelta(days=5)]

    # 📦 조합 추출
    combos = recent_5days["결과"].tolist()

    # 🔢 최근 288줄 기준 필터링 (하루 기준)
    filtered_combos = combos[-288:]

    # 🔮 예측
    top3 = predict_top3_combinations(filtered_combos)

    # 📆 현재 날짜 기준 오늘 회차 계산
    today = datetime.now().date()
    today_rows = recent_5days[recent_5days["날짜"].dt.date == today]
    current_round = len(today_rows) + 1  # 다음 회차

    return jsonify({
        "1위": top3[0],
        "2위": top3[1],
        "3위": top3[2],
        "예측 대상": f"{current_round}회차",
        "분석된 줄 수": len(filtered_combos)
    })

if __name__ == "__main__":
    app.run()
