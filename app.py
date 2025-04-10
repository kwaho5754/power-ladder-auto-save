from datetime import datetime
from random import uniform
from pathlib import Path

# Define the new upgraded app.py code
upgraded_code = '''
import os
import pandas as pd
import random
from flask import Flask, jsonify
from datetime import datetime, timedelta
from google.oauth2.service_account import Credentials
import gspread
from collections import Counter

app = Flask(__name__)

# 구글 시트 인증 설정
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4"
SHEET_NAME = "예측결과"

def load_data():
    filename = "service_account.json"
    with open(filename, "w") as f:
        f.write(SERVICE_ACCOUNT_JSON)

    creds = Credentials.from_service_account_file(filename, scopes=SCOPES)
    gc = gspread.authorize(creds)
    worksheet = gc.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    df["회차"] = pd.to_numeric(df["회차"], errors="coerce")
    df = df.dropna(subset=["회차"])
    df["회차"] = df["회차"].astype(int)
    return df

def calculate_scores(df):
    recent_days = 5
    today = datetime.today().date()
    df["날짜"] = pd.to_datetime(df["날짜"]).dt.date
    df = df[df["날짜"] >= today - timedelta(days=recent_days)]

    combos = df["결과"].tolist()
    total_lines = len(combos)

    counter = Counter(combos)

    # 패턴 기반 흐름 가중치 예시 적용 (마지막 5줄 기준)
    flow_bonus = {}
    if total_lines >= 5:
        recent = combos[-5:]
        patterns = ["→".join([c.split("T")[0].replace("LEF", "L").replace("RIGH", "R") for c in recent])]
        if "L→R→L" in patterns[0]: flow_bonus["RIGHT4EVEN"] = 2
        if "R→R→R" in patterns[0]: flow_bonus["RIGHT3ODD"] = 2

    result_scores = {}
    for combo in counter:
        base_score = counter[combo]
        bonus = flow_bonus.get(combo, 0)
        rand_factor = random.uniform(0.95, 1.1)  # 랜덤 5~10% 다양성 부여
        result_scores[combo] = (base_score + bonus) * rand_factor

    sorted_result = sorted(result_scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_result[:3]
    return top_3, total_lines, df["회차"].max()

@app.route("/predict", methods=["GET"])
def predict():
    df = load_data()
    top_3, total_lines, latest_round = calculate_scores(df)

    rank_labels = ["1위", "2위", "3위"]
    response = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {latest_round}회차)<br>"
    for i, (combo, _) in enumerate(top_3):
        label = ""
        if "LEFT3ODD" in combo: label = "좌삼홀"
        elif "LEFT3EVEN" in combo: label = "좌삼짝"
        elif "LEFT4ODD" in combo: label = "좌사홀"
        elif "LEFT4EVEN" in combo: label = "좌사짝"
        elif "RIGHT3ODD" in combo: label = "우삼홀"
        elif "RIGHT3EVEN" in combo: label = "우삼짝"
        elif "RIGHT4ODD" in combo: label = "우사홀"
        elif "RIGHT4EVEN" in combo: label = "우사짝"
        response += f"{rank_labels[i]}: {label} ({combo})<br>"

    response += f"(최근 {total_lines}줄 분석됨)"
    return response

if __name__ == "__main__":
    app.run()
'''

# Save to app.py
path = Path("/mnt/data/app.py")
path.write_text(upgraded_code)

# Output path to confirm
path.name
