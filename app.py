from flask import Flask
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import Counter

app = Flask(__name__)

@app.route("/predict", methods=["GET"])
def predict():
    # Google Sheets 인증
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('service_account.json', scope)
    client = gspread.authorize(creds)

    # 실시간결과 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    # DataFrame으로 변환
    df = pd.DataFrame(data)
    df['날짜'] = pd.to_datetime(df['날짜'])

    # ✅ 최근 5일 기준으로 필터링
    today = datetime.datetime.now().date()
    five_days_ago = today - datetime.timedelta(days=5)
    recent_df = df[df['날짜'] >= pd.to_datetime(five_days_ago)]

    # 조합 문자열 생성
    recent_df['조합'] = recent_df['좌우'] + recent_df['줄수'].astype(str) + recent_df['홀짝']

    # 가장 마지막 회차 찾기
    last_round = recent_df['회차'].max()
    target_round = last_round + 1

    # 조합 빈도수 계산
    combination_counts = Counter(recent_df['조합'])
    most_common = combination_counts.most_common(3)

    # 예측 결과 구성
    result = f"✅ 최근 5일 기준 예측 결과 (예측 대상: {target_round}회차)\n"
    for i, (combo, count) in enumerate(most_common, 1):
        result += f"{i}위: {combo}\n"
    result += f"(최근 {len(recent_df)}줄 분석됨)"

    return result

if __name__ == "__main__":
    app.run()
