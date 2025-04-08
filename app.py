from flask import Flask
import pandas as pd
import gspread
import os
import json
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/predict')
def predict():
    # 구글 인증
    SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
    service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(credentials)

    # 구글 시트 열기
    sheet = client.open("실시간결과").get_worksheet(0)  # 첫 번째 시트
    data = sheet.get_all_records()

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    # 회차가 숫자형이 아닐 경우 변환
    df['회차'] = pd.to_numeric(df['회차'], errors='coerce')
    df = df.dropna(subset=['회차'])
    df['회차'] = df['회차'].astype(int)

    # 최근 30줄만 사용
    recent_df = df.sort_values(by='회차', ascending=False).head(30)

    # 조합 컬럼 생성
    recent_df['조합'] = recent_df['좌우'] + recent_df['줄수'].astype(str) + recent_df['홀짝']

    # 조합별 빈도수
    counter = recent_df['조합'].value_counts()

    # 상위 3개 예측
    top3 = counter.head(3).index.tolist()

    # 현재 회차 추정 (최근 회차 + 1)
    latest_round = df['회차'].max() + 1

    # 예측 결과 문자열 구성
    result = f"""
✅ 최근 회차 기준 예측 결과  
(예측 대상: {latest_round}회차)

1위: {top3[0]}  
2위: {top3[1]}  
3위: {top3[2]}  

(최근 30줄 기준 분석)
"""
    return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    app.run()
