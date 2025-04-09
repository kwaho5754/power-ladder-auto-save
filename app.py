import os
import json
from flask import Flask
import pandas as pd
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # 구글 시트 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    service_account_json = os.environ.get('SERVICE_ACCOUNT_JSON')

    if not service_account_json:
        return "환경변수 'SERVICE_ACCOUNT_JSON'이 설정되지 않았습니다.", 500

    # 환경변수에서 불러온 JSON 문자열을 임시 파일로 저장
    with open("temp_service_account.json", "w") as f:
        f.write(service_account_json)

    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("실시간결과").worksheet("예측결과")

    # 시트 데이터 불러오기
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 최근 3일치 데이터 필터링
    today = datetime.today().date()
    three_days_ago = today - timedelta(days=3)
    df["날짜"] = pd.to_datetime(df["날짜"]).dt.date
    recent_df = df[df["날짜"] >= three_days_ago].copy()

    # 예외 처리: 데이터가 부족할 경우
    if recent_df.empty:
        return "최근 3일간 데이터가 없습니다.", 500

    # 현재 진행 중인 회차 계산
    latest_row = recent_df.iloc[-1]
    current_round = int(latest_row["회차"]) + 1

    # 조합 열 생성
    recent_df["조합"] = recent_df["좌우"] + recent_df["줄수"].astype(str) + recent_df["홀짝"]

    # 조합별 빈도수 계산
    freq = recent_df["조합"].value_counts()
    top3 = freq.head(3).index.tolist()

    result = "✅ 최근 3일 기준 예측 결과\n"
    result += f"(예측 대상: {current_round}회차)\n\n"
    for i, combo in enumerate(top3, start=1):
        result += f"{i}위: {combo}\n"
    result += f"\n(최근 {len(recent_df)}줄 분석됨)"

    return result
