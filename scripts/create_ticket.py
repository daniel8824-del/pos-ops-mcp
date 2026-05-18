"""운영 티켓 생성 — 로컬 JSONL append (강의 시연용).

학습자 환경 port:
  - GitHub Issues:  gh issue create --title ... --body ...
  - JIRA:           jira issue create ...
  - 본 스크립트는 로컬 data/tickets.jsonl 에 한 줄 append (외부 API 0건)

사용:
  python3 create_ticket.py \
    --title "POS_DOWN 강남역점 30분째" \
    --body "..." \
    --priority P2-High \
    --store SEL-001 \
    --category device
"""

import argparse
import datetime
import json
import uuid
from pathlib import Path

TICKETS = Path(__file__).parent.parent / "data" / "tickets.jsonl"

def create(title, body, priority="P3-Medium", store=None, category=None):
    ticket = {
        "ticket_id": f"OPS-{uuid.uuid4().hex[:8].upper()}",
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "title": title,
        "body": body,
        "priority": priority,
        "store_id": store,
        "category": category,
        "status": "open",
        "assignee": "unassigned",
    }
    with open(TICKETS, "a", encoding="utf-8") as f:
        f.write(json.dumps(ticket, ensure_ascii=False) + "\n")
    return ticket

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--priority", default="P3-Medium",
                   choices=["P1-Critical", "P2-High", "P3-Medium", "P4-Low"])
    p.add_argument("--store", default=None)
    p.add_argument("--category", default=None,
                   choices=["payment", "inventory", "device", "network",
                            "staff", "customer", None])
    args = p.parse_args()
    t = create(args.title, args.body, args.priority, args.store, args.category)
    print(json.dumps(t, ensure_ascii=False, indent=2))
