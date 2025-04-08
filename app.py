from flask import Flask
import gspread
import pandas as pd
import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from flask import jsonify

app = Flask(__name__)

# 환경변수에서 JSON 읽기
SERVICE_ACCOUNT_JSON = os.environ.get("SERVICE_ACCOUNT_JSON")
SERVICE_ACCOUNT_INFO = json.loads(SERVICE_ACCOUNT_JSON)

# 구글 시트 인증
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(SERVICE_ACCOUNT_INFO, scope)
client = gspread.authorize(credentials)

# 구글 시트 열기
sheet = client.open("실시간결과").worksheet("예측결과")

@app.route("/predict")
def predict():
    # 데이터 가져오기
    data = sheet.get_all_records()

    if not data:
        return "시트에 데이터가 없습니다.", 400

    df = pd.DataFrame(data)

    # 최신 30줄 기준 분석
    recent_data = df.tail(30)

    # '좌우', '줄수', '홀짝' 열이 모두 존재하는지 확인
    if not all(col in recent_data.columns for col in ['좌우', '줄수', '홀짝']):
        return "시트 열 이름 오류: '좌우', '줄수', '홀짝'이 필요합니다.", 400

    # 조합 만들기
    recent_data['조합'] = recent_data['좌우'] + recent_data['줄수'].astype(str) + recent_data['홀짝']

    # 빈도수 세기
    counts = recent_data['조합'].value_counts()

    # 가장 많이 나온 순으로 3개 선택
    top3 = counts.head(3).index.tolist()

    # 현재 회차 계산
    last_round = int(df['회차'].iloc[-1])  # 마지막 행의 회차
    current_round = last_round + 1

    # 결과 만들기
    result = f"✅ 현재 진행 중인 회차: {current_round}회차\n"
    result += "✅ 최근 회차 기준 예측 결과\n"
    for i, combo in enumerate(top3, start=1):
        result += f"{i}위: {combo}\n"
    result += "(최근 30줄 기준 분석)"

    return f"<pre>{result}</pre>"

if __name__ == "__main__":
    app.run()
