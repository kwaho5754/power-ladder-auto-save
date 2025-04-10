from flask import Flask, jsonify
import pandas as pd
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

app = Flask(__name__)


def load_sheet_data():
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive'
    ]
    json_content = os.environ.get("SERVICE_ACCOUNT_JSON")
    with open("temp_service_account.json", "w") as f:
        f.write(json_content)
    creds = ServiceAccountCredentials.from_json_keyfile_name("temp_service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("실시간결과").worksheet("예측결과")
    data = sheet.get_all_records()
    return pd.DataFrame(data)


def format_combo_name(combo):
    mapping = {
        "LEFT3ODD": "좌삼홀",
        "LEFT3EVEN": "좌삼짝",
        "LEFT4ODD": "좌사홀",
        "LEFT4EVEN": "좌사짝",
        "RIGHT3ODD": "우삼홀",
        "RIGHT3EVEN": "우삼짝",
        "RIGHT4ODD": "우사홀",
        "RIGHT4EVEN": "우사짝",
    }
    return mapping.get(combo, combo)


def determine_next_round(latest_date, latest_round):
    today = datetime.now().strftime('%Y-%m-%d')
    if latest_date < today:
        return today, 1
    else:
        return today, int(latest_round) + 1


@app.route("/predict", methods=["GET"])
def predict():
    try:
        df = load_sheet_data()
        df = df[df['날짜'] != '']

        # 최근 5일 데이터만 필터링
        df['날짜'] = pd.to_datetime(df['날짜'])
        cutoff = df['날짜'].max() - pd.Timedelta(days=4)
        df_recent = df[df['날짜'] >= cutoff]

        # 조합 생성
        df_recent['조합'] = df_recent['좌우'] + df_recent['줄수'].astype(str) + df_recent['홀짝']

        # 최근 288줄 기준
        combos = df_recent['조합'].tail(288)
        counts = combos.value_counts()

        # 순위별 예측 결과
        top_3 = counts.head(3).index.tolist()
        top_3_kor = [format_combo_name(c) for c in top_3]

        # 예측 대상 회차 계산
        latest_date = df['날짜'].max().strftime('%Y-%m-%d')
        latest_round = df[df['날짜'] == latest_date]['회차'].max()
        next_date, next_round = determine_next_round(latest_date, latest_round)

        return f"✅ 최근 5일 기준 예측 결과 (예측 대상: {next_round}회차)<br>" + \
               f"1위: {top_3_kor[0]} ({top_3[0]})<br>" + \
               f"2위: {top_3_kor[1]} ({top_3[1]})<br>" + \
               f"3위: {top_3_kor[2]} ({top_3[2]})<br><br>" + \
               f"(최근 {len(combos)}줄 분석됨)"

    except Exception as e:
        return f"❌ 오류 발생: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)