from flask import Flask
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import random

app = Flask(__name__)

# 환경 변수에서 서비스 계정 정보 불러오기
SERVICE_ACCOUNT_JSON = os.environ.get('SERVICE_ACCOUNT_JSON')
SPREADSHEET_ID = '1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4'
SHEET_NAME = '예측결과'

# 구글 시트 데이터 가져오기
def load_data():
    credentials = service_account.Credentials.from_service_account_info(
        eval(SERVICE_ACCOUNT_JSON),
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
    )
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SHEET_NAME).execute()
    values = result.get('values', [])
    df = pd.DataFrame(values[1:], columns=values[0])
    return df

# 통합 예측 로직
def predict(df):
    # 날짜 처리
    df = df[df['날짜'].str.len() > 0]  # 빈 값 제거
    df['회차'] = df['회차'].astype(int)
    df['날짜'] = pd.to_datetime(df['날짜'])
    today = pd.to_datetime(datetime.now().date())
    last_date = df['날짜'].max()
    if last_date < today:
        predict_round = 1
    else:
        predict_round = df[df['날짜'] == last_date]['회차'].max() + 1

    # 최근 5일 데이터만 분석
    recent_df = df[df['날짜'] >= today - pd.Timedelta(days=5)]

    # 분석할 조합열 생성
    recent_df['조합'] = recent_df['좌/우'] + recent_df['줄수'] + recent_df['홀/짝']

    # 최근 흐름 슬라이딩 분석 (ex: 최근 50줄 기준)
    sliding_df = recent_df.tail(50)
    sliding_counts = sliding_df['조합'].value_counts(normalize=True)

    # 전체 빈도 + 슬라이딩 + 최근 등장 안한 조합 보정
    full_counts = recent_df['조합'].value_counts(normalize=True)
    combined_score = full_counts.copy()

    for comb in full_counts.index:
        combined_score[comb] += sliding_counts.get(comb, 0) * 0.5

    # 희소 조합에 보정 점수 부여
    rare_bonus = 0.05
    low_freq = full_counts[full_counts < 0.01].index
    for comb in low_freq:
        combined_score[comb] += rare_bonus

    # 대칭 흐름 고려 (뒤집은 흐름 등장 시 가산점)
    last10 = recent_df['조합'].tail(10).tolist()
    reversed_pattern = last10[::-1]
    for idx, comb in enumerate(combined_score.index):
        if comb in reversed_pattern:
            combined_score[comb] += 0.03  # 작은 가산점

    # 예측 민감도 향상: 5~10% 랜덤 점수 부여
    for comb in combined_score.index:
        combined_score[comb] += random.uniform(0.05, 0.1)

    # 점수 상위 3개 추출
    top3 = combined_score.sort_values(ascending=False).head(3).index.tolist()

    # 매핑
    name_map = {
        'LEFT3EVEN': '좌삼짝',
        'RIGHT3ODD': '우삼홀',
        'LEFT4ODD': '좌사홀',
        'RIGHT4EVEN': '우사짝',
    }

    result = []
    for idx, comb in enumerate(top3):
        label = name_map.get(comb, comb)
        result.append(f"{idx+1}위: {label} ({comb})")

    줄수 = len(recent_df)
    return predict_round, result, 줄수

# 웹페이지로 결과 표시
@app.route('/predict')
def predict_route():
    try:
        df = load_data()
        predict_round, result, 줄수 = predict(df)
        return f"""
        ✅ 최근 5일 기준 예측 결과 (예측 대상: {predict_round}회차)<br>
        {'<br>'.join(result)}<br>
        (최근 {줄수}줄 분석됨)
        """
    except Exception as e:
        return f"❌ 오류 발생: {e}"

if __name__ == '__main__':
    app.run()
