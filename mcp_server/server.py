"""pos-ops MCP 서버 — stdio MCP (Copilot CLI / Claude Code 호환).

3 tool 노출:
  - get_logs(store, status, limit)
  - detect_anomaly(window_min, store)
  - create_ticket(title, body, priority, store, category)

학습자 환경 (Copilot CLI 또는 Claude Code) mcp.json 설정 예시:
  {
    "mcpServers": {
      "pos-ops": {
        "command": "python3",
        "args": ["/path/to/pos-ops-mock/mcp/server.py"]
      }
    }
  }
"""

import subprocess
import json
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

ROOT = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

mcp = FastMCP("pos-ops")


def _run(script, args):
    """script 실행 후 stdout JSON 파싱."""
    result = subprocess.run(
        ["python3", str(SCRIPTS / script), *args],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


@mcp.tool()
def get_logs(store: str = None, status: str = None, limit: int = 20) -> list:
    """최근 POS 거래 로그를 조회한다.

    Args:
        store: 매장 ID (예: SEL-001). None이면 전체 매장.
        status: 거래 상태 필터 (OK / POS_DOWN / PAYMENT_FAIL /
                STOCK_SHORTAGE / REFUND / TERMINAL_TIMEOUT).
        limit: 반환 최대 건수 (기본 20).
    """
    args = ["--limit", str(limit)]
    if store: args += ["--store", store]
    if status: args += ["--status", status]
    return _run("get_logs.py", args)


@mcp.tool()
def detect_anomaly(window_min: int = 60, store: str = None) -> dict:
    """최근 window_min분간 거래에서 이상 케이스를 집계한다.

    반환: {window_min, since, now, total, anomalies, by_store, top_issue}

    Args:
        window_min: 분석 윈도우 분 단위 (기본 60).
        store: 단일 매장만 분석하려면 매장 ID 지정.
    """
    args = ["--window", str(window_min)]
    if store: args += ["--store", store]
    return _run("detect_anomaly.py", args)


@mcp.tool()
def create_ticket(
    title: str,
    body: str,
    priority: str = "P3-Medium",
    store: str = None,
    category: str = None,
) -> dict:
    """운영 티켓을 생성한다 (data/tickets.jsonl append).

    Args:
        title: 티켓 제목 한 줄.
        body: 본문 (재현 절차 · 영향 매장 · 임시 조치 등).
        priority: P1-Critical / P2-High / P3-Medium / P4-Low.
        store: 영향 매장 ID (선택).
        category: payment / inventory / device / network / staff / customer.
    """
    args = ["--title", title, "--body", body, "--priority", priority]
    if store: args += ["--store", store]
    if category: args += ["--category", category]
    return _run("create_ticket.py", args)


if __name__ == "__main__":
    mcp.run(transport="stdio")
