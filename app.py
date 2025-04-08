from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/predict')
def predict():
    # 구글 인증
    SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
    service_account_info = json.loads(SERVICE_ACCOUNT_JSON)
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(credentials)

    # 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 날짜 필터링 (최근 3일)
    df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    recent_days = datetime.now() - timedelta(days=3)
    df = df[df['날짜'] >= recent_days]

    if df.empty:
        return "❗최근 3일 이내 데이터가 없어 예측을 실행할 수 없습니다.", 200, {'Content-Type': 'text/plain; charset=utf-8'}

    # 최근 회차 기준 분석
    df = df.sort_values(by='회차')
    df['회차'] = pd.to_numeric(df['회차'], errors='coerce')
    df = df.dropna(subset=['회차'])
    df['회차'] = df['회차'].astype(int)

    df['조합'] = df['좌우'] + df['줄수'].astype(str) + df['홀짝']
    top3 = df['조합'].value_counts().head(3).index.tolist()
    current_round = df['회차'].max() + 1

    result = f"""
✅ 최근 3일 기준 예측 결과  
(예측 대상: {current_round}회차)

1위: {top3[0]}  
2위: {top3[1]}  
3위: {top3[2]}  
(최근 {len(df)}줄 분석됨)
"""
    return result, 200, {'Content-Type': 'text/plain; charset=utf-8'}

if __name__ == '__main__':
    app.run()
