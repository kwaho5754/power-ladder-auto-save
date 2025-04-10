from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    result = {
        "1위": "RIGHT3ODD",
        "2위": "LEFT3EVEN",
        "3위": "RIGHT4EVEN",
        "최근 분석줄 수": 288,
        "예측 대상 회차": 289
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
