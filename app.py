import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, jsonify
from collections import Counter
from datetime import datetime

app = Flask(__name__)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
with open("service_account.json", "w") as f:
    f.write(SERVICE_ACCOUNT_JSON)
credentials = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(credentials)
sheet = gc.open("실시간결과").worksheet("예측결과")

# 조합 키 생성 함수
def make_comb(row):
    return f"{row['좌우']}{row['줄수']}{row['홀짝']}"

# 점수 계산 함수 (기본 빈도 기반 + 희소도 보정 등 추가 가능)
def calculate_scores(combs):
    counter = Counter(combs)
    total = sum(counter.values())
    score_dict = {}
    for comb, count in counter.items():
        freq_score = count / total
        rare_bonus = 0.05 if count < 5 else 0  # 잘 안나온 조합 가산점
        score_dict[comb] = freq_score + rare_bonus
    return score_dict

@app.route("/predict", methods=["GET"])
def predict():
    try:
        # 데이터프레임 불러오기
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # 열 이름 정리
        df.columns = ['날짜', '회차', '좌우', '줄수', '홀짝']
        df = df.dropna()

        # 날짜 기준 최근 5일 필터링
        df['날짜'] = pd.to_datetime(df['날짜'])
        cutoff_date = pd.to_datetime(datetime.now().date()) - pd.Timedelta(days=5)
        recent_df = df[df['날짜'] >= cutoff_date]

        # 조합 열 추가
        recent_df['조합'] = recent_df.apply(make_comb, axis=1)
        all_combs = recent_df['조합'].tolist()

        # 점수 계산 및 상위 3개 선택 (4개 중 3개 맞추는 시스템 배팅 방식 전초 작업)
        score_dict = calculate_scores(all_combs)
        top_combs = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)[:3]

        # 현재 회차 계산 (마지막 날짜 + 1)
        today = df['날짜'].max().date()
        today_df = df[df['날짜'].dt.date == today]
        max_round = today_df['회차'].max()
        next_round = max_round + 1 if not pd.isna(max_round) else 1

        # 결과 구성
        result = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {next_round}회차)<br>"
        for i, (comb, _) in enumerate(top_combs):
            label = {
                'LEFT3ODD': '좌삼홀', 'LEFT3EVEN': '좌삼짝',
                'LEFT4ODD': '좌사홀', 'LEFT4EVEN': '좌사짝',
                'RIGHT3ODD': '우삼홀', 'RIGHT3EVEN': '우삼짝',
                'RIGHT4ODD': '우사홀', 'RIGHT4EVEN': '우사짝'
            }.get(comb, comb)
            result += f"{i+1}위: {label} ({comb})<br>"

        result += f"(최근 {len(recent_df)}줄 분석됨)"
        return result

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
