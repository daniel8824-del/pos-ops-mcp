"""SessionStart hook ③ | 세션 시작 시 어제 운영 요약 brief.

발동 시점: Claude Code / Copilot CLI 세션 시작 직후
역할: 어제 매장별 거래 + 이상 비율 + 미해결 티켓 top 3 요약 출력

실전 port:
  - 사내 KPI DB / Datadog / Grafana API 호출
  - on-call 교대 자동 알림 (오전 8시 등)
"""

import sys
import json
import csv
import datetime
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"

def yesterday_summary():
    txn_file = DATA / "transactions.csv"
    if not txn_file.exists():
        return None

    # transactions.csv의 최신 ts를 "오늘"로 간주 (시뮬레이션 vault)
    latest = None
    with open(txn_file, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = datetime.datetime.fromisoformat(row["ts"])
            if latest is None or ts > latest:
                latest = ts
    if not latest:
        return None

    yesterday = (latest - datetime.timedelta(days=1)).date()

    total, anomaly = 0, 0
    revenue = 0
    by_store = defaultdict(lambda: {"total": 0, "anomaly": 0, "revenue": 0})

    with open(txn_file, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = datetime.datetime.fromisoformat(row["ts"])
            if ts.date() != yesterday:
                continue
            total += 1
            by_store[row["store_id"]]["total"] += 1
            if row["status"] != "OK":
                anomaly += 1
                by_store[row["store_id"]]["anomaly"] += 1
            try:
                amt = int(row["amount_krw"])
                revenue += amt
                by_store[row["store_id"]]["revenue"] += amt
            except ValueError:
                pass

    # 매장별 이상 비율 Top 3
    rates = [
        (sid, s["anomaly"] / s["total"] if s["total"] else 0, s)
        for sid, s in by_store.items()
    ]
    rates.sort(key=lambda x: x[1], reverse=True)
    top3 = rates[:3]

    return {
        "date": yesterday.isoformat(),
        "total": total,
        "anomaly": anomaly,
        "anomaly_rate": anomaly / total if total else 0,
        "revenue_krw": revenue,
        "top3_problematic": [
            {"store_id": sid, "rate": rate, "anomaly": s["anomaly"], "total": s["total"]}
            for sid, rate, s in top3
        ],
    }

def main():
    summary = yesterday_summary()
    if not summary:
        return

    msg = (
        f"☀ [HOOK] Morning Brief | {summary['date']}\n"
        f"  거래 {summary['total']:,} · 매출 ₩{summary['revenue_krw']:,} · "
        f"이상 {summary['anomaly_rate']*100:.1f}%\n"
        f"  주의 매장 Top 3 (이상 비율):\n"
    )
    for s in summary["top3_problematic"]:
        msg += f"    - {s['store_id']}  {s['rate']*100:.1f}% ({s['anomaly']}/{s['total']})\n"
    msg += "  → morning-report skill 또는 anomaly-triage 권장"

    print(msg)

if __name__ == "__main__":
    main()
