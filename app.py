from flask import Flask
import pandas as pd
import gspread
from datetime import datetime, timedelta
from collections import Counter
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__)

# 구글 시트 연동 설정
SERVICE_ACCOUNT_JSON = os.getenv('SERVICE_ACCOUNT_JSON')
info = json.loads(SERVICE_ACCOUNT_JSON)
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_info(info, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("실시간결과").worksheet("예측결과")

@app.route('/predict')
def predict():
    data = sheet.get_all_values()
    headers, rows = data[0], data[1:]
    df = pd.DataFrame(rows, columns=headers)

    # 날짜 변환
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['회차'] = df['회차'].astype(int)

    # ✅ 최근 5일 기준 데이터만 추출
    today = datetime.now().date()
    recent_df = df[df['날짜'] >= pd.Timestamp(today - timedelta(days=5))]

    # ✅ 진행 중인 회차 계산
    today_df = df[df['날짜'] == pd.Timestamp(today)]
    if today_df.empty:
        current_round = 1
    else:
        max_round_today = today_df['회차'].max()
        current_round = int(max_round_today) + 1
    current_round_text = f"✅ 현재 진행 중인 회차: {current_round}회차"

    # ✅ 조합 문자열 생성
    recent_df['조합'] = recent_df['좌/우'] + recent_df['줄수'] + recent_df['홀/짝']

    # ✅ 슬라이딩 분석 (마지막 30줄)
    recent_combinations = recent_df['조합'].tolist()
    last_30 = recent_combinations[-30:] if len(recent_combinations) >= 30 else recent_combinations
    freq_30 = Counter(last_30).most_common()

    # ✅ 전체 분석 (최근 5일)
    all_freq = Counter(recent_combinations)

    # ✅ 예외 조합 감지 (출현 적은 조합도 일부 포함)
    all_combinations = list(set(recent_df['조합'].unique()))
    rare = [x for x in all_combinations if all_freq[x] <= 2]

    # ✅ 상위 추천 조합 결정 (자주 등장 + 희귀 조합 포함)
    top_candidates = [x for x, _ in freq_30[:2]]  # 상위 2개
    if rare:
        top_candidates.append(rare[0])  # 출현 적은 조합 중 하나 포함

    # ✅ 결과 포맷
    result_lines = [
        f"✅ 최근 5일 기준 예측 결과 (예측 대상: {current_round}회차)",
        f"1위: {top_candidates[0] if len(top_candidates) > 0 else '-'}",
        f"2위: {top_candidates[1] if len(top_candidates) > 1 else '-'}",
        f"3위: {top_candidates[2] if len(top_candidates) > 2 else '-'}",
        f"(최근 {len(recent_combinations)}줄 분석됨)",
    ]

    return "<br>".join([current_round_text] + result_lines)

if __name__ == '__main__':
    app.run()
