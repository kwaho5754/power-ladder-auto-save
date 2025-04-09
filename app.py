from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from collections import Counter

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # 구글 시트 인증
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    if not data:
        return "시트에 데이터가 없습니다."

    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()  # 🔥 열 이름 공백 제거 (중요!)

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df = df.dropna(subset=["날짜"])

    # 최근 5일 기준 필터링
    today = datetime.now().date()
    recent_df = df[df["날짜"] >= pd.Timestamp(today - timedelta(days=5))]

    # 분석 대상 회차 추정
    if recent_df.empty:
        return "최근 5일간 데이터가 없습니다."
    recent_df = recent_df.sort_values("회차")
    next_round = recent_df["회차"].max() + 1

    # 조합 열 생성
    recent_df["조합"] = (
        recent_df["좌/우"].astype(str).str.strip() +
        recent_df["줄 수"].astype(str).str.strip() +
        recent_df["홀/짝"].astype(str).str.strip()
    )

    # 조합별 빈도수 분석
    combo_counts = Counter(recent_df["조합"])
    top_3 = combo_counts.most_common(3)

    result_html = "<br>✅ 최근 5일 기준 예측 결과 (예측 대상: {}회차)<br>".format(next_round)
    for i, (combo, count) in enumerate(top_3, 1):
        result_html += "{}위: {}<br>".format(i, combo)

    result_html += "(최근 {}줄 분석됨)".format(len(recent_df))
    return result_html

if __name__ == "__main__":
    app.run()
