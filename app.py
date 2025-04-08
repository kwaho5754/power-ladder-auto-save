from flask import Flask
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 환경 변수에서 서비스 계정 JSON 가져오기
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        raise ValueError("환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.")
    
    # JSON 문자열을 파일로 저장
    with open("service_account.json", "w") as f:
        f.write(service_account_json)

    # 구글 시트 인증 및 열기
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # 시트 열기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    if not data:
        return "시트에 데이터가 없습니다."

    df = pd.DataFrame(data)

    # 최근 30줄 기준으로 분석
    recent_data = df.tail(30)

    # 조합 문자열 생성 (예: RIGHT3EVEN)
    recent_data["조합"] = recent_data["좌우"] + recent_data["줄수"].astype(str) + recent_data["홀짝"]

    # 조합 빈도수 집계
    counts = recent_data["조합"].value_counts()

    top3 = counts.head(3).index.tolist()
    
    # 현재 회차 = 시트 마지막 회차 + 1
    last_round = df["회차"].max()
    current_round = int(last_round) + 1

    result_text = f"""✅ 최근 회차 기준 예측 결과 (예상 회차: {current_round})
1위: {top3[0]}
2위: {top3[1]}
3위: {top3[2]}
(최근 30줄 기준 분석)"""

    return f"<pre>{result_text}</pre>"
