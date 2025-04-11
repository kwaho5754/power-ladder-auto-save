from flask import Flask, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from flask_cors import CORS
import os
import json
from collections import Counter

app = Flask(__name__)
CORS(app)

# 서비스 계정 JSON 설정
SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_ACCOUNT_JSON')
with open("service_account.json", "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)

# 시트 연결
sheet = client.open_by_key("1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4")
worksheet = sheet.worksheet("실시간결과")

def make_combo(row):
    return f"{row['좌우']}{row['줄수']}{row['홀짝']}"

# 고급 통계 기반 예측
def analyze_and_predict():
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if len(df) < 10:
        return {"message": "데이터가 부족합니다."}

    df["조합"] = df.apply(make_combo, axis=1)
    df = df[-288:]  # 최근 288줄 (하루 기준)

    # 빈도수 기반 조합 분석
    counter = Counter(df["조합"])
    most_common = counter.most_common()

    top3 = [combo for combo, _ in most_common[:3]]
    return {
        "최근_조합_빈도": dict(most_common[:10]),
        "1위": top3[0] if len(top3) > 0 else "",
        "2위": top3[1] if len(top3) > 1 else "",
        "3위": top3[2] if len(top3) > 2 else ""
    }

# 머신러닝 기반 예측
def predict_with_ml():
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)

    if len(df) < 21:
        return "데이터 부족"

    df["조합"] = df.apply(make_combo, axis=1)
    df["target"] = df["조합"].shift(-1)
    df = df.dropna()

    df = df[-21:]  # 최근 20줄 + 타겟

    X = df[["좌우", "줄수", "홀짝"]]
    y = df["target"]

    X = pd.get_dummies(X)
    model = DecisionTreeClassifier()
    model.fit(X, y)

    latest = df[["좌우", "줄수", "홀짝"]].iloc[-1:]
    latest = pd.get_dummies(latest)
    latest = latest.reindex(columns=X.columns, fill_value=0)

    pred = model.predict(latest)[0]
    return pred

@app.route("/predict", methods=["GET"])
def predict():
    result = analyze_and_predict()
    ml_result = predict_with_ml()
    result["머신러닝_예측결과"] = ml_result
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
