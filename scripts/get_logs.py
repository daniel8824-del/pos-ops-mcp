"""최근 거래 로그 N건 또는 시간 범위로 조회.

사용:
  python3 get_logs.py --limit 20
  python3 get_logs.py --store SEL-001 --status PAYMENT_FAIL --limit 10
"""

import csv
import json
import argparse
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "transactions.csv"

def get(limit=20, store=None, status=None):
    rows = []
    with open(DATA, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if store and row["store_id"] != store:
                continue
            if status and row["status"] != status:
                continue
            rows.append(row)
    rows.sort(key=lambda r: r["ts"], reverse=True)
    return rows[:limit]

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--store", default=None)
    p.add_argument("--status", default=None)
    args = p.parse_args()
    print(json.dumps(get(args.limit, args.store, args.status), ensure_ascii=False, indent=2))
