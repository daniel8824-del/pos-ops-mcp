"""PreToolUse hook ② — create_ticket 호출 전 가드레일.

발동 시점: mcp__pos-ops__create_ticket tool 호출 직전
역할:
  - title 길이 5자 미만 → 차단 (의미 없는 티켓 방지)
  - P1-Critical 우선순위인데 body 길이 30자 미만 → 차단 (사유 부실 방지)
  - 동일 store + 동일 category 5분 내 중복 생성 시도 → 경고 (간단 dedup)

실전 port:
  - SQL injection / SSRF 같은 위험 패턴 차단
  - 외부 ticketing 시스템 권한 검증
  - 운영자 휴가/교대 여부 확인 후 assignee 자동 변경
"""

import sys
import json
import datetime
from pathlib import Path

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

args = payload.get("tool_args", {}) or payload.get("input", {})
title = args.get("title", "")
body = args.get("body", "")
priority = args.get("priority", "P3-Medium")
store = args.get("store")
category = args.get("category")

errors = []
if len(title) < 5:
    errors.append(f"title 너무 짧음 ({len(title)}자) — 5자 이상 필요")
if priority == "P1-Critical" and len(body) < 30:
    errors.append(f"P1-Critical은 body 30자 이상 필요 (현재 {len(body)}자)")

# 5분 내 중복 dedup
TICKETS = Path(__file__).parent.parent / "data" / "tickets.jsonl"
if TICKETS.exists() and store and category:
    now = datetime.datetime.now()
    with open(TICKETS, encoding="utf-8") as f:
        for line in f:
            try:
                t = json.loads(line)
            except Exception:
                continue
            if t.get("store_id") == store and t.get("category") == category:
                try:
                    t_at = datetime.datetime.fromisoformat(t["created_at"])
                except Exception:
                    continue
                if (now - t_at).total_seconds() < 300:
                    errors.append(
                        f"5분 내 동일 store+category 티켓 존재: {t['ticket_id']}"
                    )
                    break

if errors:
    print(json.dumps({
        "decision": "block",
        "reason": "  ".join(errors),
    }))
    sys.exit(2)   # exit 2 = block (Claude Code 표준)

# OK — 통과
sys.exit(0)
