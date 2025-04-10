from flask import Flask, jsonify
import pandas as pd
from datetime import datetime

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # ▶️ Google Sheets에서 불러온 데이터
    sheet_url = "https://docs.google.com/spreadsheets/d/1HXRIbAOEotWONqG3FVT9iub9oWNANs7orkUKjmpqfn4/export?format=csv&gid=0"
    df = pd.read_csv(sheet_url)

    # ▶️ 최근 날짜 기준으로 5일치 데이터 필터링
    df["날짜"] = pd.to_datetime(df["날짜"])
    recent_date = df["날짜"].max()
    five_days_ago = recent_date - pd.Timedelta(days=5)
    df_filtered = df[df["날짜"] >= five_days_ago]

    # ▶️ 조합 컬럼 생성 (예: RIGHT3ODD)
    df_filtered["조합"] = (
        df_filtered["좌우"] + df_filtered["줄수"].astype(str) + df_filtered["홀짝"]
    )

    # ▶️ 조합별 빈도수 집계
    combo_counts = df_filtered["조합"].value_counts()

    # ▶️ 가장 많이 나온 상위 3개 조합 추출
    top3 = combo_counts.head(3).index.tolist()

    # ✅ 최신 회차 계산 (자정 지나면 1회차로 초기화)
    today = datetime.now().strftime("%Y-%m-%d")
    last_date = df["날짜"].iloc[-1].strftime("%Y-%m-%d")
    last_round = int(df["회차"].iloc[-1])

    if last_date != today:
        latest_round = 1
    else:
        latest_round = last_round + 1

    # ▶️ 결과 반환
    result = {
        "✅ 최근 5일 기준 예측 결과": f"(예측 대상: {latest_round}회차)",
        "1위": top3[0],
        "2위": top3[1] if len(top3) > 1 else None,
        "3위": top3[2] if len(top3) > 2 else None,
        "📊 분석 줄 수": len(df_filtered),
    }
    return jsonify(result)
