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
    # ✅ 환경변수에서 서비스 계정 정보 불러와 JSON 파일로 저장
    service_account_content = os.getenv("SERVICE_ACCOUNT_JSON")
    if not service_account_content:
        return "SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다.", 500

    with open("service_account.json", "w") as f:
        f.write(service_account_content)

    # 구글 시트 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)

    # 시트 열기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    # 데이터프레임 변환 및 날짜 처리
    df = pd.DataFrame(data)
    df['날짜'] = pd.to_datetime(df['날짜'])

    # ✅ 최근 5일 기준 필터링
    today = datetime.datetime.now().date()
    five_days_ago = today - datetime.timedelta(days=5)
    recent_df = df[df['날짜'] >= pd.to_datetime(five_days_ago)]

    # 조합 문자열 생성
    recent_df['조합'] = recent_df['좌우'] + recent_df['줄수'].astype(str) + recent_df['홀짝']

    # 가장 마지막 회차 번호
    last_round = recent_df['회차'].max()
    target_round = last_round + 1

    # 조합 빈도수 계산
    combination_counts = Counter(recent_df['조합'])
    most_common = combination_counts.most_common(3)

    # 결과 문자열 구성
    result = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {target_round}회차) "
    for i, (combo, count) in enumerate(most_common, 1):
        result += f"{i}위: {combo} "
    result += f"(최근 {len(recent_df)}줄 분석됨)"

    return result

if __name__ == "__main__":
    app.run()
