from flask import Flask
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from collections import Counter
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 구글 시트 인증
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)

    # 시트 열기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 날짜 컬럼이 datetime 형식으로 인식되도록 변환
    df['날짜'] = pd.to_datetime(df['날짜'])

    # 최근 3일치 데이터 필터링
    three_days_ago = datetime.now() - timedelta(days=3)
    recent_df = df[df['날짜'] >= three_days_ago]

    # 회차 계산 (날짜가 바뀌면 1회차부터 다시 시작되도록)
    latest_date = df['날짜'].max()
    today_rounds = df[df['날짜'] == latest_date]['회차']
    latest_round = today_rounds.max()
    target_round = latest_round + 1

    # 최근 줄 기준 분석용 문자열 생성
    recent_df['조합'] = recent_df['좌우'] + recent_df['줄수'].astype(str) + recent_df['홀짝']
    combination_counts = Counter(recent_df['조합'])
    top3 = combination_counts.most_common(3)

    # 결과 HTML 생성
    result = "<p>✅ 최근 3일 기준 예측 결과<br>"
    result += f"(예측 대상: {target_round}회차)<br><br>"
    for i, (combo, count) in enumerate(top3):
        result += f"{i+1}위: {combo}<br>"
    result += f"<br>(최근 {len(recent_df)}줄 분석됨)</p>"

    return result

if __name__ == "__main__":
    app.run(debug=True)