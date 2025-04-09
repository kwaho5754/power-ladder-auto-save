from flask import Flask
import pandas as pd
import datetime
import gspread
import os
import json
from collections import Counter
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/predict-advanced", methods=["GET"])
def predict_advanced():
    # ✅ 서비스 계정 JSON 환경변수 처리
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    if not service_account_json:
        return "환경변수 SERVICE_ACCOUNT_JSON이 없습니다.", 500

    with open("service_account.json", "w") as f:
        f.write(service_account_json)

    # ✅ 구글 시트 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # ✅ 날짜 및 회차 정리
    df["날짜"] = pd.to_datetime(df["날짜"])
    df = df.sort_values(by=["날짜", "회차"])

    # ✅ 최근 5일치 데이터 필터링
    today = datetime.datetime.now()
    five_days_ago = today - datetime.timedelta(days=5)
    recent_df = df[df["날짜"] >= five_days_ago].copy()

    if recent_df.empty:
        return "최근 5일 데이터가 없습니다.", 500

    recent_df["조합"] = recent_df["좌우"] + recent_df["줄수"].astype(str) + recent_df["홀짝"]

    # ✅ 슬라이딩 패턴 분석 (최근 3개 조합이 과거에 얼마나 나왔는가)
    sliding_window = 3
    recent_patterns = list(recent_df["조합"][-sliding_window:])
    pattern_str = "-".join(recent_patterns)

    full_pattern_list = ["-".join(recent_df["조합"].iloc[i:i+sliding_window])
                         for i in range(len(recent_df)-sliding_window)]
    sliding_count = Counter(full_pattern_list)
    sliding_score = sliding_count.get(pattern_str, 0)

    # ✅ 대칭 흐름 분석 (예: A → B → C → B → A)
    reverse_pattern = recent_patterns[::-1]
    reverse_str = "-".join(reverse_pattern)
    symmetry_score = full_pattern_list.count(reverse_str)

    # ✅ 희귀 조합 감지 (잘 안 나오는 조합을 가장 낮은 빈도로 1개 포함)
    rare_combo = Counter(recent_df["조합"]).most_common()[-1][0]

    # ✅ 속성별 개별 예측
    lr = recent_df["좌우"].value_counts().idxmax()
    lc = recent_df["줄수"].astype(str).value_counts().idxmax()
    oe = recent_df["홀짝"].value_counts().idxmax()
    decomposed_combo = lr + lc + oe

    # ✅ 상위 조합 2개 + 희귀 조합 1개 출력
    top_combos = [combo for combo, _ in Counter(recent_df["조합"]).most_common(2)]
    top_combos.append(rare_combo)

    # ✅ 다음 회차 추정
    latest_date = recent_df["날짜"].max()
    today_df = recent_df[recent_df["날짜"] == latest_date]
    next_round = int(today_df["회차"].max()) + 1 if not today_df.empty else 1

    result = f"""
✅ [고급 분석 예측 결과]
예측 대상: {next_round}회차

🔹 추천 조합:
1위: {top_combos[0]}
2위: {top_combos[1]}
3위 (희귀): {top_combos[2]}

🔹 속성별 추정 조합: {decomposed_combo}
🔹 슬라이딩 흐름 반복 횟수: {sliding_score}회
🔹 대칭 흐름 감지: {symmetry_score}회
(최근 {len(recent_df)}줄 기준 분석됨)
"""
    return result, 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(debug=True)
