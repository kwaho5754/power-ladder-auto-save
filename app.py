from flask import Flask, jsonify, request
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

# 🔮 상위 3개 조합 예측
def predict_top3_combinations(data):
    count = Counter(data)
    top3 = [item[0] for item in count.most_common(3)]
    return top3

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # 📥 시트에서 CSV 가져오기
        sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSdr7sw0pVmKV3LUw5EAAoYo6IbMn_bOJfRP-ED9XCRPRtOPbWALiJ1dnESrxGlsQ/pub?gid=0&single=true&output=csv"
        df = pd.read_csv(sheet_url)

        df.dropna(subset=["결과"], inplace=True)

        # 🧹 날짜 필터 (최근 5일)
        df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
        recent_5days = df[df["날짜"] >= pd.Timestamp.now() - pd.Timedelta(days=5)]

        # 📊 분석할 조합만 추출
        combos = recent_5days["결과"].tolist()
        filtered_combos = combos[-288:]  # 하루 회차 기준

        # 🔮 예측
        top3 = predict_top3_combinations(filtered_combos)

        # ⏱ 오늘 날짜 기준 회차 계산
        today = datetime.now().date()
        today_rows = recent_5days[recent_5days["날짜"].dt.date == today]
        current_round = len(today_rows) + 1

        return jsonify({
            "1위": top3[0],
            "2위": top3[1],
            "3위": top3[2],
            "예측 대상": f"{current_round}회차",
            "분석된 줄 수": len(filtered_combos)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ✅ 예측 결과를 외부에서 받아 저장 (POST)
@app.route("/receive-predict", methods=["POST"])
def receive_predict():
    data = request.json
    print("🔔 예측 결과 수신 완료!")
    print("📦 받은 데이터:", data)
    return jsonify({"message": "예측 결과를 성공적으로 수신했습니다."})

if __name__ == "__main__":
    app.run()
