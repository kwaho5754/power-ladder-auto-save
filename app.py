from flask import Flask, request, jsonify

app = Flask(__name__)

# 예측 결과를 보여주는 기본 웹 페이지
@app.route('/predict', methods=['GET'])
def predict():
    top_3 = ["RIGHT3ODD", "LEFT3EVEN", "RIGHT4EVEN"]  # 상위 3개 조합
    latest_round = 289  # 예측 대상 회차
    analyzed_rows = 288  # 분석에 사용된 줄 수

    return f"""
    ✅ 최근 5일 기준 예측 결과 (예측 대상: {latest_round}회차)<br>
    1위: {top_3[0]}<br>
    2위: {top_3[1]}<br>
    3위: {top_3[2]}<br>
    <br>(최근 {analyzed_rows}줄 분석됨)
    """

# 머신러닝에서 POST로 결과를 받는 엔드포인트
@app.route('/receive-predict', methods=['POST'])
def receive_prediction():
    data = request.get_json()
    print("📥 받은 예측 데이터:", data)

    return jsonify({"message": "예측 데이터 수신 성공!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
