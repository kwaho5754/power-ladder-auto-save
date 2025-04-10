from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from collections import Counter

app = Flask(__name__)

# 환경변수 기반 서비스 계정 불러오기
import os
import json

SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
filename = "service_account.json"
with open(filename, "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
client = gspread.authorize(creds)

sheet = client.open("실시간결과").worksheet("예측결과")
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ✅ 시트 열 이름에 맞게 컬럼 변경
df = df.rename(columns={
    "좌우": "좌/우",
    "줄수": "3/4",
    "홀짝": "홀/짝"
})

# ✅ 최근 5일치 데이터만 필터링
df["날짜"] = pd.to_datetime(df["날짜"])
recent_date = df["날짜"].max()
df_recent = df[df["날짜"] >= recent_date - pd.Timedelta(days=5)].copy()

# ✅ 문자열 조합으로 묶기 (예: LEFT3ODD)
df_recent["조합"] = df_recent["좌/우"] + df_recent["3/4"].astype(str) + df_recent["홀/짝"]

# ✅ 빈도 기반 상위 3개 조합 (랜덤성 부여 + 다양화)
freq = Counter(df_recent["조합"])
top3 = freq.most_common(10)

# ✅ 점수 기반 분석 + 랜덤 요소
import random
scored = []
for comb, count in top3:
    score = count + random.uniform(0.0, 1.5)  # ✅ 변동성 부여
    scored.append((comb, score))

# 점수 높은 순으로 정렬
scored.sort(key=lambda x: x[1], reverse=True)

# ✅ 결과 상위 3개
top3_result = scored[:3]

# ✅ 한글 표시로 변환
def decode_label(label):
    left_right = "좌삼짝" if label.startswith("LEFT3") else \
                 "좌사홀" if label.startswith("LEFT4") else \
                 "우삼홀" if label.startswith("RIGHT3") else \
                 "우사짝"
    return f"{left_right} ({label})"

# ✅ 현재 회차 기준 예측 대상
latest_round = df["회차"].max() + 1

@app.route("/predict")
def predict():
    try:
        res = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {latest_round}회차)<br>"
        for i, (label, score) in enumerate(top3_result, 1):
            res += f"{i}위: {decode_label(label)}<br>"
        res += f"(최근 {len(df_recent)}줄 분석됨)"
        return res
    except Exception as e:
        return f"❌ 오류 발생: {e}"

if __name__ == "__main__":
    app.run(debug=True)
