from flask import Flask
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

@app.route('/')
def index():
    return '<p>✅ Power Ladder Predictor is Running</p>'

@app.route('/run-manual')
def run_manual():
    return run_predict()

@app.route('/run-predict')
def run_predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짝": "우삼홀",
            "우삼홀": "좌삼짝",
            "좌사홀": "우사짝",
            "우사짝": "좌사홀",
        }

        all_combos = []
        valid_combos = []

        for item in data:
            time_str = item["reg_date"]
            if len(time_str) == 10:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            if (now - reg_time).total_seconds() <= 86400:
                start = item["start_point"].lower()
                line = int(item["line_count"])
                odd = item["odd_even"].lower()
                if start == "left" and line == 3 and odd == "even":
                    combo = "좌삼짝"
                elif start == "right" and line == 3 and odd == "odd":
                    combo = "우삼홀"
                elif start == "left" and line == 4 and odd == "odd":
                    combo = "좌사홀"
                elif start == "right" and line == 4 and odd == "even":
                    combo = "우사짝"
                else:
                    combo = "기타"
                all_combos.append(combo)
                if combo != "기타":
                    valid_combos.append(combo)

        valid_counter = Counter(valid_combos)
        combo_score = {
            combo: valid_counter[combo] + valid_counter.get(reverse_map.get(combo, ""), 0)
            for combo in valid_counter
        }

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        html = "<h2>🎯 예측 결과</h2>"
        for i, (combo, _) in enumerate(top3, 1):
            html += f"<p>{i}위 예측: {combo}</p>"

        html += f"<p>✅ 유효 조합 개수: {len(valid_combos)}</p>"
        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
