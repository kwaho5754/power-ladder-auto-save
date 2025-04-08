from flask import Flask
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/predict', methods=['GET'])
def predict():
    # 구글 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_dict = eval(os.environ['SERVICE_ACCOUNT_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)

    # 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 최근 30줄만 사용
    recent_data = df.tail(30)

    # 조합 생성
    recent_data['조합'] = (
        recent_data['좌우'] +
        recent_data['줄수'].astype(str) +
        recent_data['홀짝']
    )

    # 빈도수 계산
    combination_counts = recent_data['조합'].value_counts()

    # 상위 3개 조합 추출
    top_3 = combination_counts.head(3).index.tolist()

    # 가장 마지막 회차 정보 추가
    latest_round = df['회차'].max()

    # 결과 출력
    result = f"""✅ 최근 회차 기준 예측 결과 (진행 중 회차: {latest_round + 1})
1위: {top_3[0]}
2위: {top_3[1]}
3위: {top_3[2]}
(최근 30줄 기준 분석)
"""
    return result

