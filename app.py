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
    df.columns = df.columns.str.strip()  # 🔥 열 이름 공백 제거 (중요)

    # 날짜 형식 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")
    df = df.dropna(subset=["날짜"])

    # 최근 5일 필터링
    today = datetime.now().date()
    recent_df = df[df["날짜"] >= pd.Timestamp(today - timedelta(days=5))]

    if recent_df.empty:
        return "최근 5일간 데이터가 없습니다."

    recent_df = recent_df.sort_values("회차")
    next_round = recent_df["회차"].max() + 1

    # 조합 생성
    recent_df["조합"] = (
        recent_df["좌/우"].astype(str).str.strip() +
        recent_df["줄 수"].astype(str).str.strip() +
        recent_df["홀/짝"].astype(str).str.strip()
    )

    # 고급 분석: 빈도수 + 비출현 조합 보정
    combo_counts = Counter(recent_df["조합"])
    all_combos = [
        f"{lr}{num}{oe}"
        for lr in ["LEFT", "RIGHT"]
        for num in ["3", "4"]
        for oe in ["ODD", "EVEN"]
    ]
    for combo in all_combos:
        if combo not in combo_counts:
            combo_counts[combo] = 1  # 비출현 조합에도 1점 부여

    top_3 = combo_counts.most_common(3)

    result = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {next_round}회차)<br>"
    for i, (combo, count) in enumerate(top_3, 1):
        result += f"{i}위: {combo}<br>"
    result += f"(최근 {len(recent_df)}줄 분석됨)"

    return result

if __name__ == "__main__":
    app.run()
