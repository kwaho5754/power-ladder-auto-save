from flask import Flask
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from collections import Counter

app = Flask(__name__)

# 서비스 계정 JSON 파일을 환경 변수에서 가져오기
import os
import json
filename = 'service_account.json'
with open(filename, 'w') as f:
    f.write(os.environ['SERVICE_ACCOUNT_JSON'])

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
client = gspread.authorize(creds)
sheet = client.open("실시간결과").worksheet("예측결과")

@app.route("/predict")
def predict():
    data = sheet.get_all_values()
    headers = [h.strip() for h in data[0]]  # ✅ 공백 제거하여 KeyError 방지
    rows = data[1:]
    df = pd.DataFrame(rows, columns=headers)

    # 날짜 열을 datetime으로 변환
    df['날짜'] = pd.to_datetime(df['날짜'])

    # 최근 5일 기준 필터링
    today = datetime.today().date()
    recent_date = today - timedelta(days=5)
    df_recent = df[df['날짜'].dt.date >= recent_date]

    # 분석용 조합 문자열 생성
    df_recent['조합'] = df_recent['좌/우'] + df_recent['줄 수'] + df_recent['홀/짝']
    count = Counter(df_recent['조합'])
    top3 = count.most_common(3)

    # 현재 회차 추정
    df_today = df[df['날짜'].dt.date == today]
    current_round = df_today['회차'].astype(int).max() + 1 if not df_today.empty else 1

    result = f"<p>✅ 최근 5일 기준 예측 결과 (예측 대상: {current_round}회차)</p>"
    for i, (combo, _) in enumerate(top3, 1):
        result += f"<p>{i}위: {combo}</p>"
    result += f"<p>(최근 {len(df_recent)}줄 분석됨)</p>"
    return result

if __name__ == '__main__':
    app.run(debug=True)