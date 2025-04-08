from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import io
import json

app = Flask(__name__)

@app.route('/predict')
def predict():
    # 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(credentials)

    # 시트 열기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    # 최신 회차 기준으로 최근 30줄 가져오기
    recent_data = df.tail(30)

    # 조합 만들기
    recent_data['조합'] = recent_data['좌우'] + recent_data['줄수'].astype(str) + recent_data['홀짝']

    # 빈도수 계산
    counts = recent_data['조합'].value_counts()

    # 가장 많이 나온 3개 조합 추출
    top3 = counts.head(3).index.tolist()

    # 현재 회차 가져오기 (마지막 줄 기준 +1)
    try:
        last_round = int(df['회차'].iloc[-1])
        current_round = last_round + 1
    except:
        current_round = "알 수 없음"

    # 예측 결과 포맷
    result = f"""
    ✅ 최근 회차 기준 예측 결과 (예측 대상 회차: {current_round}회차)<br>
    1위: {top3[0]}<br>
    2위: {top3[1]}<br>
    3위: {top3[2]}<br>
    (최근 30줄 기준 분석)
    """
    return result

if __name__ == '__main__':
    app.run()
