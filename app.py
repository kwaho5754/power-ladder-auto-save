from flask import Flask
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

# 예측 조합 추출 함수
def extract_combination(item):
    start = str(item["start_point"]).lower()
    line = int(item["line_count"])
    odd = str(item["odd_even"]).lower()

    if start == "left" and line == 3 and odd == "even":
        return "좌삼짝"
    elif start == "right" and line == 3 and odd == "odd":
        return "우삼홀"
    elif start == "left" and line == 4 and odd == "odd":
        return "좌사홀"
    elif start == "right" and line == 4 and odd == "even":
        return "우사짝"
    else:
        return "기타"

@app.route("/run-predict")
def run_predict():
    try:
        # 실시간 데이터 가져오기
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        # 조합 분석
        reverse_map = {
            "좌삼짝": "우삼홀",
            "우삼홀": "좌삼짝",
            "좌사홀": "우사짝",
            "우사짝": "좌사홀"
        }

        recent_results = []
        for item in data:
            reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")
            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                if combo != "기타":
                    recent_results.append(combo)

        combo_counter = Counter(recent_results)
        combo_score = {}

        for combo in combo_counter:
            base = combo_counter[combo]
            reverse = combo_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        html = f"<h2>📊 파워사다리 예측 결과 (최근 24시간)</h2>"
        for i, (combo, _) in enumerate(top3, 1):
            html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>📦 분석된 유효 조합 수: {len(recent_results)}개</p>"
        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
