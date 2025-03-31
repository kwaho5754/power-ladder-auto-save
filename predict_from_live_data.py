import requests
from datetime import datetime
from collections import Counter

# ✅ 실시간 회차 JSON에서 데이터 가져오기
url = "https://ntry.com/data/json/games/power_ladder/recent_result.json"
response = requests.get(url)
data = response.json()

print(f"\n[🔄 분석 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
print(f"📦 총 회차 수집됨: {len(data)}개\n")

# ✅ 조합 추출 함수 정의
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

# ✅ 반대 이미지 정의
reverse_map = {
    "좌삼짝": "우삼홀",
    "우삼홀": "좌삼짝",
    "좌사홀": "우사짝",
    "우사짝": "좌사홀"
}

# ✅ 최근 24시간 데이터 필터링
now = datetime.now()
recent_results = []

print("📋 회차별 조합 추출 결과 (최근 20개만 표시):")

# 최신 회차부터 정렬
sorted_data = sorted(data, key=lambda x: int(x.get("date_round", 0)), reverse=True)

shown_count = 0  # 콘솔 출력 개수 제한

for item in sorted_data:
    time_str = item["reg_date"]
    if " " in time_str:
        reg_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    else:
        reg_time = datetime.strptime(time_str, "%Y-%m-%d")

    if (now - reg_time).total_seconds() <= 86400:
        combo = extract_combination(item)
        round_num = item.get("date_round", "?")
        reg_date = item.get("reg_date", "?")

        # ✅ 최근 20개만 콘솔에 출력
        if shown_count < 20:
            print(f"  - {reg_date} / {round_num}회차 → 조합: {combo}")
            shown_count += 1

        # ✅ 전체 분석에는 모든 조합 포함
        if combo != "기타":
            recent_results.append(combo)

# ✅ 등장 빈도 분석 + 반대 조합 포함
combo_counter = Counter(recent_results)
combo_score = {}

for combo in combo_counter:
    base = combo_counter[combo]
    reverse = combo_counter.get(reverse_map.get(combo, ""), 0)
    combo_score[combo] = base + reverse

# ✅ 상위 3개 조합 예측 출력
top3 = sorted(combo_score.items(), key=lambda x: x[1], reverse=True)[:3]

print(f"\n✅ 분석에 사용된 유효한 조합 수: {len(recent_results)}개")

print("\n📊 최근 24시간 기준 분석 결과 (본인 + 반대 포함):")
if combo_score:
    for combo, score in combo_score.items():
        print(f"  - {combo}: {score}회")

    print("\n🎯 예측 결과 (최근 24시간 분석 기반)")
    for i, (combo, _) in enumerate(top3, start=1):
        print(f"  ✅ {i}위 예측: {combo}")
else:
    print("⚠️ 유효한 조합이 없어 예측할 수 없습니다.")
