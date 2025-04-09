import os
import json
import pandas as pd
import datetime
from flask import Flask
from collections import Counter
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # STEP 1: 서비스 계정 환경변수 → JSON 저장
    json_data = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not json_data:
        return "❌ 환경변수 'SERVICE_ACCOUNT_JSON' 없음"
    with open("service_account.json", "w") as f:
        f.write(json_data)

    # STEP 2: 구글 시트 연결
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])

    # STEP 3: 컬럼명 정리
    df.columns = df.columns.str.strip().str.replace(" ", "").str.replace("/", "").str.replace("\u200b", "")
    df.rename(columns={
        "날짜": "날짜",
        "회차": "회차",
        "좌우": "좌우",
        "줄수": "줄수",
        "홀짝": "홀짝"
    }, inplace=True)

    # STEP 4: 최근 5일 데이터 필터링
    df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')
    today = datetime.datetime.now().date()
    cutoff = today - datetime.timedelta(days=5)
    df = df[df["날짜"] >= pd.Timestamp(cutoff)]

    # STEP 5: 조합 생성
    df["조합"] = df["좌우"].str.strip() + df["줄수"].str.strip() + df["홀짝"].str.strip()

    # STEP 6: 최근 300줄 기준 분석
    분석대상 = df.tail(300)
    counter = Counter(분석대상["조합"])
    top_3 = counter.most_common(3)

    # STEP 7: 회차 계산
    try:
        last_round = df["회차"].astype(int).max()
        predict_round = last_round + 1
    except:
        predict_round = "?"

    # STEP 8: 결과 출력
    lines = []
    lines.append("✅ 최근 5일 기준 예측 결과")
    lines.append(f"(예측 대상: {predict_round}회차)")
    for i, (combo, count) in enumerate(top_3, 1):
        lines.append(f"{i}위: {combo}")
    lines.append(f"(최근 {len(분석대상)}줄 분석됨)")
    
    return "\n".join(lines)

if __name__ == "__main__":
    app.run()
