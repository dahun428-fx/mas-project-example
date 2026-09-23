
import sqlite3
import sys

from mini_mas.trace import DB_PATH


def q(conn, sql, *args):
    return conn.execute(sql, args).fetchall()


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    conn = sqlite3.connect(DB_PATH)

    traces = q(conn, "SELECT trace_id FROM traces GROUP BY trace_id ORDER BY MAX(id) DESC LIMIT ?", limit)
    if not traces:
        print("기록이 없습니다. 먼저 질문을 몇 개 실행하세요.")
        return
    ids = [t[0] for t in traces]
    placeholders = ",".join("?" * len(ids))

    total = q(conn, f"""
        SELECT COUNT(DISTINCT trace_id), COUNT(*), SUM(cost_usd), SUM(input_tokens), SUM(output_tokens)
        FROM traces WHERE trace_id IN ({placeholders})""", *ids)[0]
    turns, calls, cost, tok_in, tok_out = total

    print(f"최근 {turns} 턴 · LLM 호출 {calls}회 · 턴당 {calls / turns:.1f}회")
    print(f"총 비용 ${cost:.5f} · 턴당 ${cost / turns:.5f}")
    print(f"토큰 입력 {tok_in:,} / 출력 {tok_out:,}\n")

    print("담당별")
    print(f"{'agent':<12}{'호출':>5}{'비용($)':>12}{'평균ms':>9}{'출력토큰':>10}")
    for agent, n, c, ms, out in q(conn, f"""
        SELECT agent, COUNT(*), SUM(cost_usd), AVG(latency_ms), SUM(output_tokens)
        FROM traces WHERE trace_id IN ({placeholders})
        GROUP BY agent ORDER BY SUM(cost_usd) DESC""", *ids):
        print(f"{agent:<12}{n:>5}{c:>12.5f}{ms:>9.0f}{out:>10,}")

    latencies = [r[0] for r in q(conn, f"""
        SELECT SUM(latency_ms) FROM traces WHERE trace_id IN ({placeholders})
        GROUP BY trace_id ORDER BY SUM(latency_ms)""", *ids)]
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95) - 1] if len(latencies) > 1 else latencies[0]
    print(f"\n턴 LLM 시간 합계  p50 {p50:.0f}ms · p95 {p95:.0f}ms")

    errors = q(conn, f"SELECT COUNT(*) FROM traces WHERE trace_id IN ({placeholders}) AND error IS NOT NULL", *ids)[0][0]
    truncated = q(conn, f"SELECT COUNT(*) FROM traces WHERE trace_id IN ({placeholders}) AND finish_reason='length'", *ids)[0][0]
    print(f"오류 {errors}건 · 답변 잘림(length) {truncated}건")

    print("\n최근 턴 상세")
    for trace_id in ids[:3]:
        rows = q(conn, "SELECT seq, agent, model, latency_ms, cost_usd FROM traces WHERE trace_id=? ORDER BY seq", trace_id)
        head = q(conn, "SELECT query FROM traces WHERE trace_id=? ORDER BY seq LIMIT 1", trace_id)[0][0]
        print(f"\n  [{trace_id}] {head[:50]}...")
        for seq, agent, model, ms, c in rows:
            print(f"    {seq}. {agent:<12} {model:<22} {ms:>6.0f}ms  ${c:.6f}")


if __name__ == "__main__":
    main()
