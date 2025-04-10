from flask import Flask, request
import datetime

app = Flask(__name__)

# 예측 결과를 저장할 전역 변수
latest_prediction = {
    "target_round": None,
    "top3": [],
    "analyzed_rows": 0,
    "timestamp": None
}

def format_combo_name(combo):
    mapping = {
        "LEFT3ODD": "좌삼홀",
        "LEFT3EVEN": "좌삼짝",
        "LEFT4ODD": "좌사홀",
        "LEFT4EVEN": "좌사짝",
        "RIGHT3ODD": "우삼홀",
        "RIGHT3EVEN": "우삼짝",
        "RIGHT4ODD": "우사홀",
        "RIGHT4EVEN": "우사짝"
    }
    return mapping.get(combo, combo)

@app.route("/receive-predict", methods=["POST"])
def receive_predict():
    data = request.get_json()
    if not data:
        return {"error": "No data received"}, 400

    # 예측 결과 저장
    latest_prediction["target_round"] = data.get("target_round")
    latest_prediction["top3"] = data.get("top3", [])
    latest_prediction["analyzed_rows"] = data.get("analyzed_rows", 0)
    latest_prediction["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {"message": "Prediction received successfully."}, 200

@app.route("/predict", methods=["GET"])
def predict():
    if not latest_prediction["top3"]:
        return "❌ 예측 결과가 아직 없습니다. Colab에서 먼저 예측을 실행해 주세요."

    result = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {latest_prediction['target_round']}회차)<br>"
    for i, combo in enumerate(latest_prediction["top3"], start=1):
        result += f"{i}위: {format_combo_name(combo)} ({combo})<br>"
    result += f"<br>(최근 {latest_prediction['analyzed_rows']}줄 분석됨, {latest_prediction['timestamp']} 분석)"
    return result

if __name__ == '__main__':
    app.run(debug=True)
