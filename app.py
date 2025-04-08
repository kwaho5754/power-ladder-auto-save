import os
import json
import pandas as pd
import gspread
from flask import Flask
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route("/predict")
def predict():
    # 구글 인증
    service_account_info = json.loads(os.environ["SERVICE_ACCOUNT_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    # 시트 불러오기
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)

    # 예측에 사용할 열 이름
    col_mapping = {
        "좌우": "start_point",
        "줄수": "line_count",
        "홀짝": "odd_even"
    }

    recent_data = df.rename(columns=col_mapping)
    recent_count = 30
    recent_data = recent_data.tail(recent_count)

    # 조합 문자열 생성
    recent_data["조합"] = (
        recent_data["start_point"] +
        recent_data["line_count"].astype(str) +
        recent_data["odd_even"]
    )

    # 빈도수 계산
    top3 = recent_data["조합"].value_counts().head(3).index.tolist()

    # 진행 중인 회차 = 현재 최대 회차 + 1
    df = df.sort_values(by="회차", ascending=True)
    current_round = df["회차"].max() + 1

    # 결과 출력
    return f"""
    ✅ 최근 회차 기준 예측 결과<br>
    현재 진행 중인 회차: {current_round}회<br>
    1위: {top3[0]}<br>
    2위: {top3[1]}<br>
    3위: {top3[2]}<br>
    (최근 {recent_count}줄 기준 분석)
    """

if __name__ == "__main__":
    app.run()
