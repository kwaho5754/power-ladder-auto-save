import os
import json
import datetime
import pandas as pd
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 인증
    json_data = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
    client = gspread.authorize(creds)

    # 구글 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_values()

    # 데이터프레임 구성
    df = pd.DataFrame(data[1:], columns=data[0])
    df = df[df['날짜'] != '']  # 빈 행 제거

    # 날짜 + 회차 기준 정렬
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['회차'] = df['회차'].astype(int)
    df = df.sort_values(by=['날짜', '회차'])

    # 현재 날짜 및 회차 추정
    today = datetime.datetime.now().date()
    latest_date = df['날짜'].max().date()
    today_df = df[df['날짜'].dt.date == latest_date]
    latest_round = today_df['회차'].max()

    # 예측 대상 회차 = 최신 회차 + 1
    target_round = latest_round + 1 if latest_round < 288 else 1
    base_date = latest_date if latest_round < 288 else latest_date + datetime.timedelta(days=1)

    # 최근 5일 데이터 필터링
    start_date = base_date - datetime.timedelta(days=5)
    recent_df = df[df['날짜'].dt.date >= start_date]

    # ----------------------------- 고급 분석 -----------------------------
    recent_df['조합'] = recent_df[['좌우', '줄수', '홀짝']].agg(''.join, axis=1)
    combos = recent_df['조합'].tolist()

    counter = Counter(combos)
    most_common = counter.most_common()

    # ✅ 슬라이딩 흐름 분석 (최근 50줄)
    sliding_df = recent_df.tail(50)
    sliding_combos = sliding_df['조합'].tolist()
    sliding_counter = Counter(sliding_combos)
    sliding_top = [x[0] for x in sliding_counter.most_common()]

    # ✅ 좌우 패턴 반복 감지
    pattern_sequence = ''.join(sliding_df['좌우'].tolist())
    reversed_seq = pattern_sequence[::-1]
    repeated = []

    for i in range(3, 8):
        if reversed_seq[:i] == reversed_seq[i:2 * i]:
            repeated.append(reversed_seq[:i])

    # ✅ 최근 안 나온 조합 우선
    all_combos = ['LEFT3ODD', 'LEFT3EVEN', 'LEFT4ODD', 'LEFT4EVEN',
                  'RIGHT3ODD', 'RIGHT3EVEN', 'RIGHT4ODD', 'RIGHT4EVEN']
    never_seen = [c for c in all_combos if c not in counter]

    # ✅ 속성 분해 기반 빈도 분석
    right_left = Counter(recent_df['좌우'])
    line_num = Counter(recent_df['줄수'])
    odd_even = Counter(recent_df['홀짝'])

    # 조합 재구성 점수
    combo_score = {}
    for c in all_combos:
        lr = c[:5]
        ln = c[5]
        oe = c[6:]
        score = (
            right_left[lr] +
            line_num[ln] +
            odd_even[oe] +
            (5 if c in sliding_top else 0) +
            (5 if any(r in c for r in repeated) else 0) +
            (7 if c in never_seen else 0)
        )
        combo_score[c] = score

    sorted_combos = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)
    top3 = [x[0] for x in sorted_combos[:3]]

    # HTML 반환
    html = f"""
    ✅ 최근 5일 기준 예측 결과 (예측 대상: {target_round}회차)<br>
    1위: {top3[0]}<br>
    2위: {top3[1]}<br>
    3위: {top3[2]}<br>
    (최근 {len(recent_df)}줄 분석됨)
    """
    return html

if __name__ == "__main__":
    app.run(debug=True)
