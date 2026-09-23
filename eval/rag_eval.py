

from mini_mas.rag import Retriever
from mini_mas.trace import flush, new_trace

CASES = [
    ("공복혈당 정상 범위는?", "K01"),
    ("당뇨 전단계 기준이 뭐야?", "K01"),
    ("총콜레스테롤 240이면 높은 거야?", "K02"),
    ("나쁜 콜레스테롤이 뭐야?", "K03"),
    ("좋은 콜레스테롤 기준은?", "K04"),
    ("고혈압 진단 기준", "K05"),
    ("콜레스테롤 낮추는 음식", "K06"),
    ("혈당 올리지 않는 식사법", "K07"),
    ("혈압 낮추는 운동", "K08"),
    ("검진 전에 금식해야 해?", "K09"),
    ("주의 판정이 무슨 뜻이야?", "K10"),
    ("오늘 점심 뭐 먹지", None),
]


def main():
    retriever = Retriever()
    top1 = 0
    top3 = 0
    misses = []

    for query, expected in CASES:
        new_trace(query)  # 질의 1건 = trace 1건. 안 하면 전부 "-" 로 뭉친다
        hits = retriever.search(query)
        ids = [h["id"] for h in hits]

        if expected is None:
            ok = len(hits) == 0
            if ok:
                top1 += 1
                top3 += 1
            else:
                misses.append((query, "검색 결과 없어야 함", ids))
            continue

        if ids[:1] == [expected]:
            top1 += 1
        if expected in ids:
            top3 += 1
        else:
            misses.append((query, expected, ids))

    n = len(CASES)
    print(f"top-1 정확도: {top1}/{n} = {top1 / n:.1%}")
    print(f"top-3 적중률: {top3}/{n} = {top3 / n:.1%}")

    if misses:
        print("\n틀린 문항:")
        for query, expected, ids in misses:
            print(f"  {query!r}  기대={expected}  실제={ids}")


if __name__ == "__main__":
    main()
    flush()  # 데몬 스레드라 프로그램이 먼저 끝나면 기록이 날아간다
