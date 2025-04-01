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
        return "그림"
    elif start == "right" and line == 3 and odd == "odd":
        return "우삼홀"
    elif start == "left" and line == 4 and odd == "odd":
        return "좌삼홀"
    elif start == "right" and line == 4 and odd == "even":
        return "우삼징"
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
            "좌삼홀": "우삼징",
            "우삼홀": "좌삼홀",
            "좌삼징": "우삼홀",
            "우삼징": "좌삼징"
        }

        all_combos = []
        valid_combos = []
        recent_items = []
        time_round_combo_list = []

        for item in data:
            time_str = str(item["reg_date"])
            round_ = item.get("round", "??회차")

            if len(time_str) == 10:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d")
            else:
                reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

            if (now - reg_time).total_seconds() <= 86400:
                combo = extract_combination(item)
                all_combos.append(combo)
                time_round_combo_list.append((time_str[:10], round_, combo))
                if combo != "기타":
                    valid_combos.append(combo)
                    recent_items.append((time_str[:10], round_, combo))

        all_counter = Counter(all_combos)
        valid_counter = Counter(valid_combos)

        html = "<h2>현재 24시간 기준 배열 결과</h2>"
        for combo in ["좌삼홀", "우삼홀", "좌삼징", "우삼징"]:
            valid_count = valid_counter.get(combo, 0)
            total_count = all_counter.get(combo, 0)
            html += f"<p> - {combo}: {valid_count}회 (전체: {total_count}회)</p>"

        # 패턴 분석 점수화
        combo_score = {}
        for combo in valid_counter:
            base = valid_counter[combo]
            reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
            combo_score[combo] = base + reverse

        # 연속 출현 점수 추가 (1번)
        last_combo = None
        streaks = Counter()
        for combo in valid_combos:
            if combo == last_combo:
                streaks[combo] += 1
            else:
                streaks[combo] = 1
            last_combo = combo
        for combo in streaks:
            combo_score[combo] += streaks[combo]

        # 출현 주기 점수 추가 (2번)
        last_seen = {}
        interval_score = Counter()
        for idx, combo in enumerate(valid_combos):
            if combo in last_seen:
                interval = idx - last_seen[combo]
                interval_score[combo] += int(20 / (interval + 1))
            last_seen[combo] = idx
        for combo in interval_score:
            combo_score[combo] += interval_score[combo]

        # 반대 패턴 빈도 가중치 (3번)
        for combo in valid_counter:
            opposite = reverse_map.get(combo, "")
            combo_score[combo] += valid_counter.get(opposite, 0)

        # 줄 수 반영 (4번)
        line_counter = Counter()
        for item in data:
            line = int(item["line_count"])
            if (now - datetime.strptime(item["reg_date"], "%Y-%m-%d %H:%M:%S")).total_seconds() <= 86400:
                line_counter[line] += 1
        top_line = line_counter.most_common(1)[0][0] if line_counter else 3
        if top_line == 4:
            for combo in combo_score:
                if "짝" in combo:
                    combo_score[combo] += 2

        top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

        html += "<h2>혈외 결과 (24시간 배열 기반)</h2>"
        for i, (combo, _) in enumerate(top3, 1):
            html += f"<p> {i}위 예측: <b>{combo}</b></p>"

        html += f"<p>\u2705 유효 조합 개수: {len(valid_combos)}</p>"

        html += "<h3>\ud604재 24시간 전체 결과 출력</h3>"
        for date, round_, combo in reversed(time_round_combo_list):
            html += f"<p>- {date} / {round_} ➞ 조합: {combo}</p>"

        return html

    except Exception as e:
        return f"<p>\uc624류 발생: {e}</p>"

if __name__ == "__main__":
    app.run(debug=True)
