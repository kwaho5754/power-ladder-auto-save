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
        return "좌삼짹"
    elif start == "right" and line == 3 and odd == "odd":
        return "우삼홀"
    elif start == "left" and line == 4 and odd == "odd":
        return "좌사홀"
    elif start == "right" and line == 4 and odd == "even":
        return "우사짹"
    else:
        return "기타"

@app.route("/run-predict")
def run_predict():
    try:
        url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
        response = requests.get(url)
        data = response.json()
        now = datetime.now()

        reverse_map = {
            "좌삼짹": "우사홀",
            "우삼홀": "좌삼짹",
            "좌사홀": "우사짹",
            "우사짹": "좌사홀"
        }

        all_combos = []
        valid_combos = []

        for item in data:
            reg_time = datetime.strptime(item["reg_date"], "%Y-%m-%d") if len(item["reg_date"]) == 10 else datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")
            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)
                if combo != "기타":
                    valid_combos.append(combo)

        html = "<h2>현재 24시간 기준 배후 결과 (본인 + 반대 포함)</h2>"
        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)
        for combo in ["좌삼짹", "우삼홀", "좌사홀", "우사짹"]:
            html += f"<p>- {combo}: {valid_counter[combo]}회 (전체: {all_counter[combo]}회)</p>"

        html += "<h2>형태변화 구조 기본 예측 결과</h2>"

        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base * 2 + reverse  # 복합 평가

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]
        for i, (combo, score) in enumerate(top3, 1):
            html += f"<p>✅ {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>\n후복 조합 수 (전체): {len(valid_combos)} / 전체: {len(all_combos)}</p>"

        # 고급 패턴 분석 (288회 기준)
        html += "<h2>패턴 협칙 구조 분석</h2>"

        def find_longest_sequence(seq, target):
            max_len = count = 0
            for item in seq:
                if item == target:
                    count += 1
                    max_len = max(max_len, count)
                else:
                    count = 0
            return max_len

        # 패턴 리스트 만들기
        pattern_analysis = {
            "포함 형태": [],
            "혼지지 패턴": [],
            "좌/우 패턴": [],
            "3/4줄 패턴": []
        }

        directions = []
        lines = []
        odds = []

        for item in data:
            if (now - datetime.strptime(item["reg_date"], "%Y-%m-%d" if len(item["reg_date"]) == 10 else "%Y-%m-%d %H:%M:%S")).total_seconds() <= 86400:
                directions.append(item["start_point"].lower())
                lines.append(item["line_count"])
                odds.append(item["odd_even"].lower())

        max_odd = find_longest_sequence(odds, "odd")
        max_even = find_longest_sequence(odds, "even")
        max_left = find_longest_sequence(directions, "left")
        max_right = find_longest_sequence(directions, "right")
        max_3 = find_longest_sequence(lines, 3)
        max_4 = find_longest_sequence(lines, 4)

        html += f"<p>혼: {max_odd}회 연속 / 지: {max_even}회 연속</p>"
        html += f"<p>좌보: {max_left}회 연속 / 우보: {max_right}회 연속</p>"
        html += f"<p>3줄: {max_3}회 연속 / 4줄: {max_4}회 연속</p>"

        return html

    except Exception as e:
        return f"<p>오류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
