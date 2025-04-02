from flask import Flask
import requests
from datetime import datetime
from collections import Counter

app = Flask(__name__)

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

@app.route("/run-manual")
def run_predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짝": "우삼홀",
            "우삼홀": "좌사홀",
            "좌사홀": "우사짝",
            "우사짝": "좌삼짝",
        }

        all_combos = []
        valid_combos = []
        recent_items = []

        for item in data:
            time_str = str(item["reg_date"])
            if len(time_str) == 10:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)
                if combo != "기타":
                    valid_combos.append(combo)
                    recent_items.append((item.get("reg_date", "??"), item.get("round", "??회차"), combo))

        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)

        html = "<h2>🎯 시스템 배팅용 예측 (최근 24시간 기준)</h2>"
        html += "<p>선택된 3개 조합 중 2개 이상 적중 시 성공!</p>"

        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        for combo, score in top3:
            html += f"<p>✅ {combo}</p>"

        html += f"<br><p>✅ 유효한 조합 개수: {len(valid_combos)} / 전체: {len(all_combos)}</p>"

        html += "<h2>📜 24시간 전체 결과 출력 (최신이 위에)</h2>"
        for reg_date, round_, combo in reversed(recent_items):
            html += f"<p>- {reg_date} / {round_} ➜ 조합: {combo}</p>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
