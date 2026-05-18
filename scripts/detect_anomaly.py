"""최근 window_min분 거래 로그에서 이상 케이스 집계.

사용:
  python3 detect_anomaly.py --window 60 [--store SEL-001]

출력 (JSON):
  {
    "window_min": 60,
    "since": "2026-05-14T08:00:00",
    "total": 234,
    "anomalies": {
      "POS_DOWN": 12,
      "PAYMENT_FAIL": 8,
      ...
    },
    "by_store": { ... },
    "top_issue": "POS_DOWN"
  }
"""

import csv
import json
import argparse
import datetime
from collections import defaultdict
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "transactions.csv"

# 거래 데이터의 최신 시점을 "현재"로 간주 (시뮬레이션 vault)
def latest_ts():
    with open(DATA, encoding="utf-8") as f:
        latest = None
        for row in csv.DictReader(f):
            ts = datetime.datetime.fromisoformat(row["ts"])
            if latest is None or ts > latest:
                latest = ts
    return latest

def detect(window_min=60, store=None):
    now = latest_ts()
    cutoff = now - datetime.timedelta(minutes=window_min)

    anomalies = defaultdict(int)
    by_store = defaultdict(lambda: defaultdict(int))
    total = 0

    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ts = datetime.datetime.fromisoformat(row["ts"])
            if ts < cutoff:
                continue
            if store and row["store_id"] != store:
                continue
            total += 1
            status = row["status"]
            if status != "OK":
                anomalies[status] += 1
                by_store[row["store_id"]][status] += 1

    top_issue = max(anomalies, key=anomalies.get) if anomalies else None

    return {
        "window_min": window_min,
        "since": cutoff.isoformat(),
        "now": now.isoformat(),
        "total": total,
        "anomalies": dict(anomalies),
        "by_store": {k: dict(v) for k, v in by_store.items()},
        "top_issue": top_issue,
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--window", type=int, default=60)
    p.add_argument("--store", default=None)
    args = p.parse_args()
    print(json.dumps(detect(args.window, args.store), ensure_ascii=False, indent=2))
