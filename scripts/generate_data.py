"""POS 운영 시뮬레이션 데이터 생성기.

산출:
  data/stores.csv       전국 10 매장 (좌표·브랜드·운영시간)
  data/products.csv     아모레 30 SKU (브랜드·카테고리·가격)
  data/transactions.csv 3일 × 매장당 일 800건 = ~24K rows
  data/incidents.csv    과거 운영 티켓 50건

이상 케이스 5종 자동 주입:
  POS 다운 5% / 결제 실패 3% / 재고 부족 2% / 환불 1% / 단말 timeout 2%

공개 정보 + 시뮬레이션 — 실제 아모레 운영 데이터 아님.
"""

import csv
import random
import datetime
from pathlib import Path

random.seed(42)  # 결정론적 재현

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ────────────────────────────────────────────────────────────
# 1. 매장 10곳 — 공개 도시 좌표 기반
# ────────────────────────────────────────────────────────────

STORES = [
    {"store_id": "SEL-001", "name": "강남역점",   "brand": "이니스프리",  "region": "서울", "lat": 37.4979, "lng": 127.0276, "open": "09:00", "close": "22:00"},
    {"store_id": "SEL-002", "name": "명동점",     "brand": "아모레스토어", "region": "서울", "lat": 37.5636, "lng": 126.9826, "open": "10:00", "close": "22:00"},
    {"store_id": "SEL-003", "name": "홍대점",     "brand": "에뛰드",      "region": "서울", "lat": 37.5563, "lng": 126.9236, "open": "11:00", "close": "23:00"},
    {"store_id": "GYG-001", "name": "분당서현점", "brand": "라네즈",      "region": "경기", "lat": 37.3850, "lng": 127.1230, "open": "10:00", "close": "22:00"},
    {"store_id": "BSN-001", "name": "서면점",     "brand": "아리따움",    "region": "부산", "lat": 35.1577, "lng": 129.0594, "open": "10:00", "close": "22:00"},
    {"store_id": "DGU-001", "name": "동성로점",   "brand": "이니스프리",  "region": "대구", "lat": 35.8693, "lng": 128.5950, "open": "10:00", "close": "22:00"},
    {"store_id": "ICN-001", "name": "구월점",     "brand": "에뛰드",      "region": "인천", "lat": 37.4490, "lng": 126.7050, "open": "10:00", "close": "22:00"},
    {"store_id": "GWJ-001", "name": "충장로점",   "brand": "아리따움",    "region": "광주", "lat": 35.1466, "lng": 126.9220, "open": "10:00", "close": "22:00"},
    {"store_id": "DJN-001", "name": "둔산점",     "brand": "라네즈",      "region": "대전", "lat": 36.3504, "lng": 127.3845, "open": "10:00", "close": "22:00"},
    {"store_id": "USN-001", "name": "삼산점",     "brand": "아모레스토어", "region": "울산", "lat": 35.5384, "lng": 129.3114, "open": "10:00", "close": "22:00"},
]

# ────────────────────────────────────────────────────────────
# 2. SKU 30개 — 아모레퍼시픽 공개 카탈로그 기반
# ────────────────────────────────────────────────────────────

PRODUCTS = [
    # 이니스프리
    ("INF-001", "그린티 씨드 세럼 80ml",        "이니스프리", "스킨케어",  35000),
    ("INF-002", "레티놀 시카 흔적 앰플 30ml",   "이니스프리", "앰플",      42000),
    ("INF-003", "화산송이 모공 마스크 100ml",   "이니스프리", "마스크팩",  12000),
    ("INF-004", "노세범 미네랄 파우더 5g",      "이니스프리", "메이크업",  8000),
    ("INF-005", "마이립밤 코코넛 3.5g",         "이니스프리", "립",        6500),
    ("INF-006", "그린티 클렌징 폼 150ml",        "이니스프리", "클렌징",    11000),
    # 라네즈
    ("LNZ-001", "워터뱅크 블루 하이알루로닉 세럼", "라네즈", "스킨케어",  48000),
    ("LNZ-002", "립 슬리핑 마스크 베리 20g",     "라네즈", "립케어",    24000),
    ("LNZ-003", "퍼펙트 리뉴 리제너레이터 75ml", "라네즈", "안티에이징", 78000),
    ("LNZ-004", "네오 쿠션 매트 15g 21호",      "라네즈", "쿠션",      42000),
    ("LNZ-005", "크림 스킨 토너 앤 모이스처라이저", "라네즈", "스킨케어", 38000),
    ("LNZ-006", "이데알 블러 핏 파운데이션",     "라네즈", "베이스",    38000),
    # 에뛰드
    ("ETD-001", "비비 매직 파운데이션 SPF50",   "에뛰드", "베이스",    18000),
    ("ETD-002", "플레이 컬러 아이즈 #체리블라썸", "에뛰드", "아이",      28000),
    ("ETD-003", "디어 달링 워터젤 틴트",         "에뛰드", "립",        9000),
    ("ETD-004", "드로잉 아이브로우 자동연필",    "에뛰드", "아이",      4500),
    ("ETD-005", "수분 톤업 베이스 핑크",          "에뛰드", "베이스",    16000),
    ("ETD-006", "픽싱 틴트 #장미",                "에뛰드", "립",        14000),
    # 아리따움
    ("ATM-001", "그린에디션 세럼인 토너 200ml", "아리따움", "스킨케어",  22000),
    ("ATM-002", "이데알 글로우 비비크림",        "아리따움", "베이스",    25000),
    ("ATM-003", "허니 콜라겐 마스크 5매",        "아리따움", "마스크팩",  9500),
    ("ATM-004", "쥬얼링 아이즈 #피치블라썸",     "아리따움", "아이",      18000),
    ("ATM-005", "립 페인트 매트 #누드코랄",       "아리따움", "립",        12000),
    ("ATM-006", "솝베리 클렌징 오일",             "아리따움", "클렌징",    19000),
    # 아모레스토어 / 설화수 일부
    ("ASR-001", "설화수 자음생크림 60ml",        "설화수",   "안티에이징", 235000),
    ("ASR-002", "설화수 윤조에센스 90ml",        "설화수",   "에센스",    145000),
    ("ASR-003", "헤라 블랙쿠션 15g 21호",        "헤라",     "쿠션",      78000),
    ("ASR-004", "헤라 루즈 홀릭 매트 #로지누드", "헤라",     "립",        38000),
    ("ASR-005", "아이오페 더마 리페어 크림 50ml", "아이오페", "스킨케어",  88000),
    ("ASR-006", "마몽드 로즈 워터 토너 250ml",   "마몽드",   "스킨케어",  18000),
]

# ────────────────────────────────────────────────────────────
# 3. 거래 데이터 생성 — 3일 × 매장당 일 ~800건
# ────────────────────────────────────────────────────────────

PAYMENT_METHODS = ["card", "samsung_pay", "kakao_pay", "cash", "naver_pay"]
ANOMALY_TYPES = [
    ("POS_DOWN",       0.05, "POS 단말 응답 없음 (재부팅 필요)"),
    ("PAYMENT_FAIL",   0.03, "카드 승인 거부 (한도 초과 / 카드사 오류)"),
    ("STOCK_SHORTAGE", 0.02, "재고 부족 — 판매 불가"),
    ("REFUND",         0.01, "환불 처리"),
    ("TERMINAL_TIMEOUT", 0.02, "결제 단말 timeout (>30s)"),
]

def hour_weight(h):
    """시간대별 매출 가중치 (점심·퇴근 피크)."""
    if 12 <= h <= 13: return 1.5
    if 17 <= h <= 19: return 1.7
    if 14 <= h <= 16: return 1.2
    if 20 <= h <= 21: return 1.3
    if 10 <= h <= 11: return 0.8
    if h == 9 or h == 22: return 0.5
    return 0.3

def gen_transactions(start_date, days=3):
    rows = []
    txn_id = 100000
    for day_offset in range(days):
        date = start_date + datetime.timedelta(days=day_offset)
        weekend_mult = 1.3 if date.weekday() >= 5 else 1.0
        for store in STORES:
            daily_count = int(800 * weekend_mult * random.uniform(0.85, 1.15))
            for _ in range(daily_count):
                hour = random.choices(
                    range(9, 23),
                    weights=[hour_weight(h) for h in range(9, 23)],
                )[0]
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                ts = datetime.datetime.combine(
                    date, datetime.time(hour, minute, second)
                )
                product = random.choice(PRODUCTS)
                qty = random.choices([1, 2, 3], weights=[80, 15, 5])[0]

                # 이상 케이스 주입
                anomaly = None
                rnd = random.random()
                cum = 0
                for name, rate, desc in ANOMALY_TYPES:
                    cum += rate
                    if rnd < cum:
                        anomaly = name
                        break

                status = "OK" if anomaly is None else anomaly
                amount = product[4] * qty if status in ("OK", "REFUND") else 0
                if status == "REFUND":
                    amount = -amount

                rows.append({
                    "txn_id": f"T{txn_id}",
                    "ts": ts.isoformat(),
                    "store_id": store["store_id"],
                    "product_sku": product[0],
                    "product_name": product[1],
                    "qty": qty,
                    "amount_krw": amount,
                    "payment_method": random.choice(PAYMENT_METHODS),
                    "status": status,
                })
                txn_id += 1
    return rows

# ────────────────────────────────────────────────────────────
# 4. 과거 운영 티켓 50건
# ────────────────────────────────────────────────────────────

INCIDENT_CATEGORIES = [
    ("payment",      "결제 단말 timeout 빈발"),
    ("payment",      "카드 승인 거부 — 카드사 연동 오류"),
    ("inventory",    "재고 수량 불일치 (실재고 vs 시스템)"),
    ("inventory",    "베스트셀러 SKU 품절 알림 누락"),
    ("device",       "POS 단말 갑작스러운 재부팅"),
    ("device",       "프린터 영수증 출력 실패"),
    ("device",       "바코드 스캐너 인식률 저하"),
    ("network",      "매장 인터넷 끊김 — 결제 불가 30분"),
    ("network",      "본사 동기화 지연 — 재고 정보 불일치"),
    ("staff",        "직원 권한 없음 — 환불 처리 불가"),
    ("staff",        "교대 시 POS 로그아웃 안 됨"),
    ("customer",     "고객 컴플레인 — 가격 불일치"),
]

PRIORITIES = ["P1-Critical", "P2-High", "P3-Medium", "P4-Low"]
STATUSES = ["resolved", "resolved", "resolved", "in_progress", "open"]

def gen_incidents(n=50):
    rows = []
    base = datetime.date(2026, 4, 1)
    for i in range(n):
        cat, title = random.choice(INCIDENT_CATEGORIES)
        store = random.choice(STORES)
        created = base + datetime.timedelta(days=random.randint(0, 40))
        rows.append({
            "ticket_id": f"INC-{1000 + i}",
            "created_at": created.isoformat(),
            "store_id": store["store_id"],
            "category": cat,
            "title": title,
            "priority": random.choices(PRIORITIES, weights=[5, 25, 50, 20])[0],
            "status": random.choice(STATUSES),
            "assignee": random.choice(["ops-team1", "ops-team2", "field-eng", "unassigned"]),
        })
    return rows

# ────────────────────────────────────────────────────────────
# 5. CSV 쓰기
# ────────────────────────────────────────────────────────────

def write_csv(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def main():
    write_csv(
        DATA_DIR / "stores.csv",
        STORES,
        ["store_id", "name", "brand", "region", "lat", "lng", "open", "close"],
    )
    write_csv(
        DATA_DIR / "products.csv",
        [
            {"sku": p[0], "name": p[1], "brand": p[2], "category": p[3], "price_krw": p[4]}
            for p in PRODUCTS
        ],
        ["sku", "name", "brand", "category", "price_krw"],
    )
    txns = gen_transactions(datetime.date(2026, 5, 12), days=3)
    write_csv(
        DATA_DIR / "transactions.csv",
        txns,
        ["txn_id", "ts", "store_id", "product_sku", "product_name", "qty",
         "amount_krw", "payment_method", "status"],
    )
    incs = gen_incidents(50)
    write_csv(
        DATA_DIR / "incidents.csv",
        incs,
        ["ticket_id", "created_at", "store_id", "category", "title",
         "priority", "status", "assignee"],
    )
    print(f"OK  stores.csv       {len(STORES)} rows")
    print(f"OK  products.csv     {len(PRODUCTS)} rows")
    print(f"OK  transactions.csv {len(txns)} rows")
    print(f"OK  incidents.csv    {len(incs)} rows")

if __name__ == "__main__":
    main()
