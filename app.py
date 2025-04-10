from flask import Flask, jsonify
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)

# 서비스 계정 키 JSON을 환경변수에서 불러와 저장
service_account_json = os.getenv('SERVICE_ACCOUNT_JSON')
with open("service_account.json", "w") as f:
    f.write(service_account_json)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
client = gspread.authorize(creds)

# 시트 열기
sheet = client.open("실시간결과").worksheet("예측결과")

@app.route('/predict', methods=['GET'])
def predict():
    # 시트에서 데이터 가져오기
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    # 최근 날짜 기준으로 최근 5일치 필터링
    df['날짜'] = pd.to_datetime(df['날짜'])
    recent_date = df['날짜'].max()
    date_limit = recent_date - pd.Timedelta(days=5)
    df_filtered = df[df['날짜'] >= date_limit]

    # 조합 컬럼 생성
    df_filtered['조합'] = df_filtered['좌우'] + df_filtered['줄수'].astype(str) + df_filtered['홀짝']

    # 빈도수 계산
    top_combinations = df_filtered['조합'].value_counts().head(3).index.tolist()

    # 최근 회차 확인
    last_round = df['회차'].astype(int).max()

    # 자정이 지났으면 회차는 1부터 시작
    current_hour = datetime.now().hour
    if current_hour == 0 and last_round >= 288:
        next_round = 1
    else:
        next_round = last_round + 1 if last_round < 288 else 1

    # 결과 반환
    result = {
        "1위": top_combinations[0] if len(top_combinations) > 0 else "없음",
        "2위": top_combinations[1] if len(top_combinations) > 1 else "없음",
        "3위": top_combinations[2] if len(top_combinations) > 2 else "없음",
        "예측 대상 회차": next_round,
        "최근 분석 줄 수": len(df_filtered)
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
