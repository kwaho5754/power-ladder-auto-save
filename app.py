from flask import Flask, jsonify
import pandas as pd
import random
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)

# Google Sheets 연동 설정 (환경변수에서 로딩)
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def load_sheet_data():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(os.environ['SERVICE_ACCOUNT_JSON'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def calculate_scores(df):
    # 최근 5일치 데이터 필터링
    df['날짜'] = pd.to_datetime(df['날짜'])
    cutoff_date = datetime.now() - timedelta(days=5)
    recent_df = df[df['날짜'] >= cutoff_date].copy()
    
    # 가장 최근 회차 + 1 계산
    try:
        last_round = int(recent_df['회차'].max()) + 1
    except:
        last_round = -1

    # 최근 200줄 기준 슬라이싱 (너무 과거 데이터 희석 방지)
    recent_df = recent_df.tail(200)

    # 조합 생성
    recent_df['조합'] = recent_df['좌우'] + recent_df['줄수'].astype(str) + recent_df['홀짝']
    combo_list = recent_df['조합'].tolist()

    # 빈도 기반 기본 점수
    combo_counter = Counter(combo_list)
    all_combos = [a + b + c for a in ['LEFT', 'RIGHT'] for b in ['3', '4'] for c in ['ODD', 'EVEN']]
    scores = {combo: combo_counter.get(combo, 0) for combo in all_combos}

    # 흐름 패턴 분석 점수 강화 (3~8줄 흐름 또는 좌우 대칭 감지)
    def pattern_bonus(combo):
        pattern_score = 0
        for size in range(3, 9):
            segment = combo_list[-size:]
            if segment == segment[::-1]:
                pattern_score += size * 1.5  # 대칭 보너스
        return pattern_score

    for combo in scores:
        scores[combo] += pattern_bonus(combo)

    # 동일 조합 연속 반복 패널티 부여
    if len(combo_list) >= 3 and combo_list[-1] == combo_list[-2] == combo_list[-3]:
        scores[combo_list[-1]] -= 5

    # 시스템 배팅 점수: 다른 조합과 함께 자주 등장한 조합 점수 보정
    for combo in scores:
        match_count = sum([1 for i in range(len(combo_list)-2)
                          if combo in combo_list[i:i+3]])
        scores[combo] += match_count * 0.3

    # 점수에 랜덤 요소 5~10% 부여
    for combo in scores:
        noise = random.uniform(0.95, 1.10)
        scores[combo] *= noise

    return scores, last_round, len(recent_df)

def format_combo_name(combo):
    mapping = {
        "LEFT3ODD": "좌삼홀",
        "LEFT3EVEN": "좌삼짝",
        "LEFT4ODD": "좌사홀",
        "LEFT4EVEN": "좌사짝",
        "RIGHT3ODD": "우삼홀",
        "RIGHT3EVEN": "우삼짝",
        "RIGHT4ODD": "우사홀",
        "RIGHT4EVEN": "우사짝",
    }
    return mapping.get(combo, combo)

@app.route("/predict", methods=["GET"])
def predict():
    try:
        df = load_sheet_data()
        scores, target_round, row_count = calculate_scores(df)
        sorted_combos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        top3 = sorted_combos[:3]
        result = [f"{i+1}위: {format_combo_name(combo)} ({combo})" for i, (combo, _) in enumerate(top3)]

        return (
            "✅ 최근 5일 기준 예측 결과 (예측 대상: {}회차)<br>{}<br><br>(최근 {}줄 분석됨)"
            .format(target_round, "<br>".join(result), row_count)
        )
    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)