import csv
from collections import Counter

def load_recent_data(csv_file_path, limit=50):
    """
    최근 결과 데이터를 CSV에서 읽어서 조합 문자열 리스트로 반환
    예: 좌삼짝, 우삼홀, 좌사홀 등
    """
    data = []
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # 줄 구성: start_point + line_count + odd_even
                # 예: LEFT + 3 + EVEN → 좌삼짝
                combo = convert_combo(row)
                data.append(combo)
    except Exception as e:
        print(f"❌ 파일 불러오기 오류: {e}")
    return data[-limit:]  # 최근 limit개만 반환

def convert_combo(row):
    """
    줄 하나의 데이터에서 조합 문자열 생성
    """
    side = "좌" if row["start_point"] == "LEFT" else "우"
    line = "삼" if row["line_count"] == "3" else "사"
    odd_even = "홀" if row["odd_even"] == "ODD" else "짝"
    return side + line + odd_even

def predict_result(recent_data):
    """
    최근 데이터 기반 단순 빈도 분석 → 상위 3개 조합 예측
    """
    if len(recent_data) < 3:
        return ["데이터 부족", "", ""]

    counter = Counter(recent_data)
    top3 = [item[0] for item in counter.most_common(3)]

    while len(top3) < 3:
        top3.append("")  # 부족하면 빈칸 채움

    return top3

def get_next_round(csv_file_path):
    """
    현재 저장된 마지막 회차 확인 후 +1 회차 계산
    """
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                return 1
            last_row = rows[-1]
            return int(last_row["date_round"]) + 1
    except Exception as e:
        print(f"❌ 회차 확인 오류: {e}")
        return 1

def main():
    csv_path = "예측결과.csv"  # 또는 실시간결과.csv
    recent_data = load_recent_data(csv_path)

    next_round = get_next_round(csv_path)
    rank1, rank2, rank3 = predict_result(recent_data)

    print(f"📌 예측 대상 회차: {next_round}회차")
    print(f"🔮 예측 결과")
    print(f"1위: {rank1}")
    print(f"2위: {rank2}")
    print(f"3위: {rank3}")

if __name__ == "__main__":
    main()
