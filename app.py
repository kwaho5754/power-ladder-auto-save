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
    # ✅ STEP 1: 환경변수에서 JSON 값을 받아 파일로 저장
    json_data = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not json_data:
        return "❌ 환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다."
    
    try:
        with open("service_account.json", "w") as f:
            f.write(json_data)
    except Exception as e:
        return f"❌ JSON 파일 저장 오류: {e}"

    # ✅ STEP 2: 구글 시트 연결
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])
    df.columns = df.columns.str.strip()

    # ✅ STEP 3: 최근 5일치 데이터만 사용
    df["날짜"] = pd.to_datetime(df["날짜"])
    today = datetime.datetime.now().date()
    cutoff = today - datetime.timedelta(days=5)
    df = df[df["날짜"] >= pd.Timestamp(cutoff)]

    # ✅ STEP 4: 조합 컬럼 생성
    df["조합"] = df["좌/우"].str.strip() + df["줄수"].str.strip() + df["홀/짝"].str.strip()

    # ✅ STEP 5: 최근 분석할 줄 수 설정
    분석대상 = df.tail(300)  # 최근 최대 300줄까지 사용
    counter = Counter(분석대상["조합"])
    top_3 = counter.most_common(3)

    # ✅ STEP 6: 현재 회차 추정
    try:
        last_round = df["회차"].astype(int).max()
        predict_round = last_round + 1
    except:
        predict_round = "?"

    # ✅ STEP 7: 결과 구성
    lines = []
    lines.append("✅ 최근 5일 기준 예측 결과")
    lines.append(f"(예측 대상: {predict_round}회차)")
    for i, (combo, count) in enumerate(top_3, 1):
        lines.append(f"{i}위: {combo}")
    lines.append(f"(최근 {len(분석대상)}줄 분석됨)")
    
    return "\n".join(lines)

if __name__ == "__main__":
    app.run()
