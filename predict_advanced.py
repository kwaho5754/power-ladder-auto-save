from flask import Flask
import pandas as pd
import os
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 🔹 환경 변수로부터 서비스 계정 키를 불러와 파일로 저장
    service_account_json = os.environ.get('SERVICE_ACCOUNT_JSON')
    with open('service_account.json', 'w') as f:
        f.write(service_account_json)

    # 🔹 구글 시트 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_values()
    df = pd.DataFrame(data[1:], columns=data[0])

    # 🔹 날짜 타입 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 🔹 최근 5일 기준 데이터 필터링
    today = datetime.now().date()
    five_days_ago = today - timedelta(days=5)
    recent_df = df[df["날짜"].dt.date >= five_days_ago]

    # 🔹 가장 최근 회차 번호 확인
    try:
        recent_df["회차"] = recent_df["회차"].astype(int)
        max_round = recent_df["회차"].max()
        next_round = max_round + 1
    except:
        return "❌ 회차 번호를 정수로 변환할 수 없습니다."

    # 🔹 조합 생성
    recent_df["조합"] = recent_df["좌우"] + recent_df["줄수"] + recent_df["홀짝"]

    # 🔹 조합 빈도수 세기
    counter = Counter(recent_df["조합"])
    most_common = counter.most_common(3)

    # 🔹 결과 구성
    result = f"""
✅ 최근 5일 기준 예측 결과 (예측 대상: {next_round}회차)
1위: {most_common[0][0]}
2위: {most_common[1][0]}
3위: {most_common[2][0]}
(최근 {len(recent_df)}줄 분석됨)
"""
    return result.strip()

if __name__ == "__main__":
    app.run()
