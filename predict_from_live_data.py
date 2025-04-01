import requests
from datetime import datetime
from collections import Counter

print("\n🧠 분석 시작 -", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# 실시간 데이터 불러오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

now = datetime.now()
all_combos = []
valid_combos = []

# 조합 추출 함수
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

# 회차 정보 추출
recent_items = []
for item in data:
    time_str = item["reg_date"]
    if len(time_str) == 10:
        reg_time = datetime.strptime(time_str, "%Y-%m-%d")
    else:
        reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

    if (now - reg_time).total_seconds() <= 86400:
        combo = extract_combination(item)
        item["combo"] = combo
        all_combos.append(combo)
        if combo != "기타":
            valid_combos.append(combo)
        recent_items.append(item)

print(f"📊 총 회차 수집됨: {len(recent_items)}개\n")

# 전체 회차 출력
print("📄 회차별 조합 추출 결과 (전체 표시):")
for item in recent_items[::-1]:
    print(f"- {item['reg_date'].split()[0]} / {item['date_round']}회차 ➔ 조합: {item['combo']}")

# 유효 조합 카운팅
valid_counter = Counter(valid_combos)
all_counter = Counter(all_combos)
reverse_map = {
    "좌삼짝": "우삼홀",
    "우삼홀": "좌삼짝",
    "좌사홀": "우사짝",
    "우사짝": "좌사홀"
}

print(f"\n✅ 분석에 사용된 유효한 조합 수: {len(valid_combos)}개\n")
print("📚 최근 24시간 기준 분석 결과 (본인 + 반대 포함):")
for combo in ["좌삼짝", "우삼홀", "좌사홀", "우사짝"]:
    count = valid_counter.get(combo, 0)
    total = all_counter.get(combo, 0)
    print(f"- {combo}: {count}회 (전체: {total}회)")

# 예측
combo_score = {}
for combo in valid_counter:
    base = valid_counter[combo]
    reverse = valid_counter.get(reverse_map.get(combo, ""), 0)
    combo_score[combo] = base + reverse

ranked = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

print("\n🎯 예측 결과 (최근 24시간 분석 기반)")
for i, (combo, _) in enumerate(ranked, 1):
    print(f"✅ {i}위 예측: {combo}")
