from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from collections import Counter
import os
import json
import random

app = Flask(__name__)

# 서비스 계정 인증
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
filename = "service_account.json"
with open(filename, "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
client = gspread.authorize(creds)

sheet = client.open("실시간결과").worksheet("예측결과")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# 열 이름 변경
df = df.rename(columns={"좌우": "좌/우", "줄수": "3/4", "홀짝": "홀/짝"})
df["날짜"] = pd.to_datetime(df["날짜"])
recent_date = df["날짜"].max()
df_recent = df[df["날짜"] >= recent_date - pd.Timedelta(days=5)].copy()

# 조합 생성
df_recent["조합"] = df_recent["좌/우"] + df_recent["3/4"].astype(str) + df_recent["홀/짝"]

# 빈도수 계산
freq = Counter(df_recent["조합"])
total = sum(freq.values())

# 희귀 조합 보정 점수 + 랜덤 점수 부여
scored = []
for comb, count in freq.items():
    rarity = 1.0 - (count / total)
    base_score = count
    bonus = rarity * 2.0  # 희귀 보정
    random_bonus = random.uniform(0.5, 1.5)
    score = base_score + bonus + random_bonus
    scored.append((comb, score))

scored.sort(key=lambda x: x[1], reverse=True)
top3_result = scored[:3]

# 예측 대상 회차: 가장 최근 날짜의 마지막 회차 + 1
last_day = df[df["날짜"] == recent_date]
next_round = last_day["회차"].max() + 1

# 한글로 조합 해석
def decode_label(label):
    return {
        "LEFT3ODD": "좌삼짝",
        "LEFT3EVEN": "좌삼짝",
        "LEFT4ODD": "좌사홀",
        "LEFT4EVEN": "좌사홀",
        "RIGHT3ODD": "우삼홀",
        "RIGHT3EVEN": "우삼홀",
        "RIGHT4ODD": "우사짝",
        "RIGHT4EVEN": "우사짝"
    }.get(label, "알수없음")

@app.route("/predict")
def predict():
    try:
        res = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {next_round}회차)<br>"
        for i, (label, score) in enumerate(top3_result, 1):
            res += f"{i}위: {decode_label(label)} ({label})<br>"
        res += f"(최근 {len(df_recent)}줄 분석됨)"
        return res
    except Exception as e:
        return f"❌ 오류 발생: {e}"

if __name__ == "__main__":
    app.run(debug=True)
