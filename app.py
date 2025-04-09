from flask import Flask
import pandas as pd
import datetime
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # ✅ 1. 환경변수에서 서비스 계정 JSON을 파일로 저장
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        return "환경변수 SERVICE_ACCOUNT_JSON이 설정되지 않았습니다.", 500

    with open("service_account.json", "w") as f:
        f.write(service_account_json)

    # ✅ 2. 구글 시트 인증 및 시트 연결
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    if not data:
        return "데이터가 존재하지 않습니다.", 500

    df = pd.DataFrame(data)

    # ✅ 3. 최근 5일치만 필터링
    df["날짜"] = pd.to_datetime(df["날짜"])
    five_days_ago = datetime.datetime.now() - datetime.timedelta(days=5)
    recent_df = df[df["날짜"] >= five_days_ago]

    if recent_df.empty:
        return "최근 5일 데이터가 부족합니다.", 500

    # ✅ 4. 현재 날짜와 회차 추정
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    today_df = recent_df[recent_df["날짜"] == today]

    if today_df.empty:
        current_round = 1
    else:
        current_round = today_df["회차"].max() + 1

    # ✅ 5. 조합 열 생성 및 빈도 계산
    recent_df["조합"] = recent_df["좌우"] + recent_df["줄수"].astype(str) + recent_df["홀짝"]
    freq = Counter(recent_df["조합"])
    top_3 = freq.most_common(3)

    # ✅ 6. 출력
    response = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {current_round}회차)<br>"
    for i, (combo, count) in enumerate(top_3, start=1):
        response += f"{i}위: {combo}<br>"
    response += f"(최근 {len(recent_df)}줄 분석됨)"
    return response

if __name__ == "__main__":
    app.run(debug=False)
