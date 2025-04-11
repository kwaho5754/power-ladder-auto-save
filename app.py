from flask import Flask, jsonify, Response
import pandas as pd
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# 📌 환경변수에서 JSON 추출하여 파일로 저장
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
with open("service_account.json", "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)

# 🔐 구글 시트 인증 및 불러오기
SPREADSHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(credentials)

def load_data():
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df = df[df["회차"].astype(str).str.isnumeric()]
    df["회차"] = df["회차"].astype(int)
    df["날짜"] = pd.to_datetime(df["날짜"])
    return df

def get_latest_round(df):
    now = datetime.now()
    today = now.date()
    recent = df[df["날짜"].dt.date == today]
    if recent.empty:
        return 1
    latest_round = recent["회차"].max()
    return latest_round + 1 if latest_round < 288 else 1

def analyze_top3_combinations(df):
    df["조합"] = df["좌우"] + df["줄수"].astype(str) + df["홀짝"]
    recent_df = df.tail(288)
    counts = Counter(recent_df["조합"])
    top3 = [item[0] for item in counts.most_common(3)]
    return top3, len(recent_df)

@app.route("/predict")
def predict():
    df = load_data()
    latest_round = get_latest_round(df)
    top3, used_rows = analyze_top3_combinations(df)

    html = f"""
    <h3>✅ 최근 5일 기준 예측 결과 (예측 대상: {latest_round}회차)</h3>
    <p>1위: {top3[0]}</p>
    <p>2위: {top3[1]}</p>
    <p>3위: {top3[2]}</p>
    <br>
    <small>(최근 {used_rows}줄 분석됨)</small>
    """
    return Response(html, mimetype='text/html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
