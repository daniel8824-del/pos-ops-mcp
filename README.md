# pos-ops-mcp | POS 운영 MCP 데모 (standalone)

**MCP 자체를 처음 배우는 강의용 mini 패키지.**
3 tool · 3 hook · smoke test 4개. 전부 로컬 · 외부 API 0건.

> Day 4 13차시 "MCP 개발 - 도구를 연결하는 서버" + 14차시 훅 자동화 정합.

## 구성 (1줄 설명)

```
pos-ops-mcp/
├─ data/                  시뮬레이션 4 csv (10 매장 · 30 SKU · 24K 거래)
├─ scripts/               3 함수 (get_logs · detect_anomaly · create_ticket)
├─ mcp_server/server.py   stdio MCP | 위 3 함수를 tool로 노출
├─ hooks/                 3 훅 실습 (PostToolUse · PreToolUse · SessionStart)
└─ tests/test_smoke.py    4 smoke 테스트 (3 script + MCP server)
```

## 30초 시작

```bash
# 1. venv + mcp SDK
python3 -m venv .venv && .venv/bin/pip install mcp

# 2. 데이터 생성 (1회만)
.venv/bin/python3 scripts/generate_data.py

# 3. smoke 테스트
.venv/bin/python3 tests/test_smoke.py

# 4. MCP server 단독 동작 (Ctrl+C로 종료)
.venv/bin/python3 mcp_server/server.py
```

## Claude Code / Copilot CLI 연결

`~/.claude/settings.json` 또는 프로젝트 `.claude/settings.json`:

```json
{
  "mcpServers": {
    "pos-ops": {
      "command": "/home/daniel/projects/pos-ops-mcp/.venv/bin/python3",
      "args": ["/home/daniel/projects/pos-ops-mcp/mcp_server/server.py"]
    }
  }
}
```

연결 후 학습자 자연어 한 줄:

```
"최근 1시간 이상 거래 있어? 있으면 1순위만 P2로 티켓 만들어줘"
```

→ MCP가 `detect_anomaly` → `create_ticket` 자동 chain.

## 3 Tool

| Tool | Args | 반환 |
|---|---|---|
| `get_logs` | store · status · limit | 최근 거래 N건 (시간 역순) |
| `detect_anomaly` | window_min · store | 이상 집계 + top_issue + by_store |
| `create_ticket` | title · body · priority · store · category | OPS-XXXX 신규 티켓 |

## 3 Hook 실습

학습자가 `hooks/hooks.json`을 본인 settings에 추가하면 자동 발동.
`POS_OPS_ROOT` 환경변수에 본 repo 절대 경로 지정.

| 종류 | matcher / 시점 | 역할 |
|---|---|---|
| **PostToolUse** | `mcp__pos-ops__detect_anomaly` 직후 | 임계(10건) 초과 시 운영 알림 출력 |
| **PreToolUse** | `mcp__pos-ops__create_ticket` 직전 | 가드레일 (title 5자·P1 body 30자·5분 중복) |
| **SessionStart** | 세션 시작 | 어제 운영 brief 자동 출력 |

훅 실습 시연 흐름:

```bash
# 1. 가드레일 테스트 | 짧은 title은 차단됨
echo '{"tool_args":{"title":"ab","body":"."}}' | python3 hooks/guard_ticket.py
# → exit 2 + reason

# 2. 알림 테스트 | top_issue + count payload
echo '{"tool_result":{"top_issue":"POS_DOWN","anomalies":{"POS_DOWN":15},"by_store":{"SEL-001":{}}}}' | python3 hooks/on_anomaly.py
# → "🚨 [HOOK] POS 운영 알림 ..." 출력

# 3. 세션 brief | 어제 요약 (시뮬레이션 데이터의 latest day 기준)
python3 hooks/morning_brief.py
# → "☀ [HOOK] Morning Brief | 2026-05-13 ..."
```

## 학습자 본인 환경 port (Day 5 후반)

| 항목 | 본 repo (학습용) | 실전 (학습자 본인) |
|---|---|---|
| 데이터 source | csv | 회사 POS DB · 로그 stream |
| `create_ticket` 출력 | `tickets.jsonl` | `gh issue create` / JIRA API |
| 알림 채널 | stdout | Discord · Slack · 이메일 webhook |
| 가드레일 | title 5자 | SQL injection · 권한 검증 등 |

## 데이터 출처 (정직 명시)

- 매장 좌표: 공개 도시 좌표 (실제 매장 아님)
- SKU: 아모레퍼시픽 공식 자사몰 공개 카탈로그
- 거래 패턴: 통계청 소매판매동향 + 자체 시뮬레이션
- **실제 아모레 운영 raw 데이터 아님**

## 메시지 한 줄

**"MCP는 도구 = tool · 데이터 = resource · 안내 = prompt 3 슬롯.**
**훅은 도구 호출의 전·후·시작 시점에 자동 발동하는 가드레일."**
