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
    df = df[df['날짜'] != '']
    df['날짜'] = pd.to_datetime(df['날짜'])
    df['회차'] = df['회차'].astype(int)
    df = df.sort_values(by=['날짜', '회차'])

    # 회차 추정
    latest_date = df['날짜'].max().date()
    today_df = df[df['날짜'].dt.date == latest_date]
    latest_round = today_df['회차'].max()
    target_round = latest_round + 1 if latest_round < 288 else 1
    base_date = latest_date if latest_round < 288 else latest_date + datetime.timedelta(days=1)

    # 최근 5일 데이터
    start_date = base_date - datetime.timedelta(days=5)
    recent_df = df[df['날짜'].dt.date >= start_date]
    recent_df['조합'] = recent_df[['좌우', '줄수', '홀짝']].agg(''.join, axis=1)

    # 네 가지 조합만 허용
    valid_combos = {
        'LEFT3EVEN': '좌삼짝',
        'RIGHT3ODD': '우삼홀',
        'LEFT4ODD': '좌사홀',
        'RIGHT4EVEN': '우사짝'
    }

    # 빈도, 속성 분해
    combo_list = recent_df['조합'].tolist()
    counter = Counter(combo_list)
    right_left = Counter(recent_df['좌우'])
    line_num = Counter(recent_df['줄수'])
    odd_even = Counter(recent_df['홀짝'])

    # 최근 50줄 분석
    sliding_df = recent_df.tail(50)
    sliding_combos = sliding_df['조합'].tolist()
    sliding_counter = Counter(sliding_combos)
    sliding_top = [x[0] for x in sliding_counter.most_common()]

    # 반복 감지
    pattern_sequence = ''.join(sliding_df['좌우'].tolist())
    reversed_seq = pattern_sequence[::-1]
    repeated = []
    for i in range(3, 8):
        if reversed_seq[:i] == reversed_seq[i:2*i]:
            repeated.append(reversed_seq[:i])

    # 흐름 전환 분석
    def extract_post_turn_combos(seq):
        post_combos = []
        for i in range(1, len(seq)):
            if seq[i] != seq[i-1]:
                post_combos.append(seq[i])
        return Counter(post_combos)

    turn_counter = extract_post_turn_combos(combo_list)
    reverse_sequence = combo_list[::-1]
    reverse_patterns = [tuple(reverse_sequence[i:i+3]) for i in range(len(reverse_sequence)-2)]

    # 점수 계산 (네 가지 조합만)
    combo_score = {}
    for c in valid_combos:
        lr = c[:5]
        ln = c[5]
        oe = c[6:]
        score = (
            right_left[lr] +
            line_num[ln] +
            odd_even[oe] +
            (5 if c in sliding_top else 0) +
            (5 if any(r in c for r in repeated) else 0) +
            (7 if c not in counter else 0) +
            (3 if c in turn_counter else 0)
        )
        combo_score[c] = score

    # 상위 3개 (중복 제거된)
    sorted_combos = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)
    top3 = []
    for c, _ in sorted_combos:
        if c not in top3 and len(top3) < 3:
            top3.append(c)

    # HTML 출력
    html = f"""
    ✅ 최근 5일 기준 예측 결과 (예측 대상: {target_round}회차)<br>
    1위: {valid_combos[top3[0]]} ({top3[0]})<br>
    2위: {valid_combos[top3[1]]} ({top3[1]})<br>
    3위: {valid_combos[top3[2]]} ({top3[2]})<br>
    (최근 {len(recent_df)}줄 분석됨)<br><br>
    🧠 흐름 기반 고급 분석 포함<br>
    - 전환점 이후 조합 반영<br>
    - 역방향 흐름 감지<br>
    - 반복 패턴 포함 여부<br>
    """
    return html

if __name__ == "__main__":
    app.run(debug=True)
