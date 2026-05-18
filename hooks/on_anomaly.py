"""PostToolUse hook ① — detect_anomaly 호출 후 자동 알림.

발동 시점: mcp__pos-ops__detect_anomaly tool 호출 직후
역할: top_issue count가 임계(10건) 초과면 stdout으로 운영 알림 출력
      stdout 메시지는 Claude/Copilot이 다음 turn 컨텍스트로 봄

실전 port:
  - Discord/Slack/이메일 webhook 호출 추가
  - PagerDuty / Opsgenie 같은 on-call 시스템 연동
"""

import sys
import json

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_result = payload.get("tool_result", {})
if not isinstance(tool_result, dict):
    sys.exit(0)

top_issue = tool_result.get("top_issue")
anomalies = tool_result.get("anomalies", {})

if not top_issue:
    sys.exit(0)

count = anomalies.get(top_issue, 0)
THRESHOLD = 10

if count < THRESHOLD:
    sys.exit(0)

print(
    f"🚨 [HOOK] POS 운영 알림 — TOP ISSUE {top_issue} ({count}건)\n"
    f"  영향 매장: {list(tool_result.get('by_store', {}).keys())}\n"
    f"  권장: anomaly-triage skill 실행 또는 create_ticket 호출"
)
