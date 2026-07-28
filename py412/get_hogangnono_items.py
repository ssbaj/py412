import csv
import json
import re
import sys
import time

from curl_cffi import requests

TRADE_TYPE_LABEL = {"trade": "매매", "charter": "전세", "rental": "월세", "short": "단기"}
DIRECTION_LABEL = {
    "e": "동향", "w": "서향", "s": "남향", "n": "북향",
    "se": "남동향", "sw": "남서향", "ne": "북동향", "nw": "북서향",
}
BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"


# ---------- URL 파싱 ----------

def _extract_apt_hash(addr: str) -> str:
    m = re.search(r"/apt/([^/?#]+)", addr)
    if not m:
        raise ValueError(f"addr에서 aptHash를 찾을 수 없습니다: {addr}")
    return m.group(1)


# ---------- geohash (표준 공개 알고리즘) ----------

def _geohash_encode(lat: float, lon: float, precision: int = 6) -> str:
    lat_range = [-90.0, 90.0]
    lon_range = [-180.0, 180.0]
    geohash, bit, ch, even = [], 0, 0, True
    while len(geohash) < precision:
        if even:
            mid = (lon_range[0] + lon_range[1]) / 2
            if lon > mid:
                ch |= 1 << (4 - bit)
                lon_range[0] = mid
            else:
                lon_range[1] = mid
        else:
            mid = (lat_range[0] + lat_range[1]) / 2
            if lat > mid:
                ch |= 1 << (4 - bit)
                lat_range[0] = mid
            else:
                lat_range[1] = mid
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash.append(BASE32[ch])
            bit, ch = 0, 0
    return "".join(geohash)


def _geohash_decode_bbox(geohash: str):
    lat_range, lon_range, even = [-90.0, 90.0], [-180.0, 180.0], True
    for c in geohash:
        cd = BASE32.index(c)
        for mask in (16, 8, 4, 2, 1):
            bit = 1 if cd & mask else 0
            if even:
                mid = (lon_range[0] + lon_range[1]) / 2
                lon_range[0 if bit else 1] = mid
            else:
                mid = (lat_range[0] + lat_range[1]) / 2
                lat_range[0 if bit else 1] = mid
            even = not even
    return lat_range, lon_range


def _geohashes_around(lat: float, lon: float, precision: int = 6, rings: int = 1) -> list:
    center_hash = _geohash_encode(lat, lon, precision)
    lat_range, lon_range = _geohash_decode_bbox(center_hash)
    tile_h, tile_w = lat_range[1] - lat_range[0], lon_range[1] - lon_range[0]
    clat, clon = (lat_range[0] + lat_range[1]) / 2, (lon_range[0] + lon_range[1]) / 2
    hashes = set()
    for dy in range(-rings, rings + 1):
        for dx in range(-rings, rings + 1):
            nlat = max(-90.0, min(90.0, clat + dy * tile_h))
            nlon = max(-180.0, min(180.0, clon + dx * tile_w))
            hashes.add(_geohash_encode(nlat, nlon, precision))
    return sorted(hashes)


# ---------- hogangnono API ----------

def _new_session() -> requests.Session:
    s = requests.Session(impersonate="safari")
    s.get("https://hogangnono.com/items", timeout=30)  # 익명 쿠키 발급
    return s


def _fetch_apt_detail(session: requests.Session, apt_hash: str, page_url: str) -> dict:
    r = session.get(page_url, timeout=30)
    r.raise_for_status()
    m = re.search(r'<script id="__HGNN_DATA__" type="application/json">(.*?)</script>', r.text, re.S)
    if not m:
        raise RuntimeError("페이지에서 __HGNN_DATA__를 찾을 수 없습니다.")
    detail = json.loads(m.group(1))["altState"]["AptStore"]["detail"]
    zigbang_ids = detail.get("zigbangIds") or []
    return {
        "name": detail.get("name"),
        "jibun_addr": detail.get("address"),
        "road_addr": detail.get("road_address"),
        "lat": detail.get("lat"),
        "lng": detail.get("lng"),
        "danji_ids": {int(z) for z in zigbang_ids if str(z).isdigit()},
    }


def _fetch_markers(session: requests.Session, geohashes: list, property_type: str = "apt") -> list:
    markers, seen = [], set()
    for gh in geohashes:
        r = session.get(
            "https://hogangnono.com/api/v2/items/markers",
            params={"propertyType": property_type, "geohash": gh},
            headers={"Referer": "https://hogangnono.com/items", "Accept": "application/json"},
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        if payload.get("status") != "success":
            print(f"  경고: geohash={gh} 마커 응답 오류: {payload}", file=sys.stderr)
            continue
        for mk in payload["data"]["markers"]:
            key = (mk["itemId"], mk["tradeType"])
            if key in seen:
                continue
            seen.add(key)
            markers.append(mk)
        time.sleep(0.15)
    return markers


def _fetch_item_details(session: requests.Session, markers: list) -> dict:
    """(areaHoId, tradeType_str) -> 상세정보 dict. 최대 15개씩 배치 조회."""
    details = {}
    batch_size = 15
    for i in range(0, len(markers), batch_size):
        batch = markers[i:i + batch_size]
        catalogs = [{"itemId": m["itemId"], "tradeType": m["tradeType"]} for m in batch]
        r = session.post(
            "https://hogangnono.com/api/v2/items/apt/list",
            json={"catalogs": catalogs},
            headers={
                "Referer": "https://hogangnono.com/items",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        r.raise_for_status()
        payload = r.json()
        if payload.get("status") != "success":
            print(f"  경고: apt/list 배치 {i} 응답 오류: {payload}", file=sys.stderr)
            continue
        for it in payload["data"]["items"]:
            details[(it["areaHoId"], it["tradeType"])] = it
        time.sleep(0.2)
    return details


CSV_FIELDS = [
    "areaHoId", "실매물ID", "거래유형", "단지명", "동", "층",
    "전용면적(m2)", "공급면적(m2)", "평형", "보증금/매매가(만원)", "월세(만원)",
    "매물설명", "중개사무소", "지번주소", "도로명주소", "위도", "경도",
]


def _to_row(mk: dict, it: dict) -> dict:
    sub_items = it.get("items") or [{}]
    return {
        "areaHoId": mk["itemId"],
        "실매물ID": it.get("itemId"),
        "거래유형": TRADE_TYPE_LABEL.get(mk["tradeType"], mk["tradeType"]),
        "단지명": it.get("areaDanjiName"),
        "동": it.get("dong"),
        "층": it.get("floor"),
        "전용면적(m2)": it.get("sizeM2"),
        "공급면적(m2)": it.get("sizeContractM2"),
        "평형": (it.get("roomTypeTitle") or {}).get("p"),
        "보증금/매매가(만원)": it.get("depositMin"),
        "월세(만원)": it.get("rentMin"),
        "매물설명": it.get("itemTitle"),
        "중개사무소": sub_items[0].get("agentName") if sub_items else None,
        "지번주소": None,
        "도로명주소": None,
        "위도": mk["lat"],
        "경도": mk["lng"],
    }


# ---------- 공개 함수 ----------

def get_hogangnono_items(addr: str, out_csv: str | None = None, max_rings: int = 3) -> list:
    """
    addr: 호갱노노 아파트 단지 페이지 URL
    out_csv: 지정 시 해당 경로에 CSV로도 저장. None이면 저장 안 함.
    max_rings: 단지 좌표 주변 geohash 타일 탐색 반경
    """
    apt_hash = _extract_apt_hash(addr)
    page_url = f"https://hogangnono.com/apt/{apt_hash}/0"

    session = _new_session()

    apt_info = _fetch_apt_detail(session, apt_hash, page_url)
    print(f"단지명: {apt_info['name']} / 주소: {apt_info['jibun_addr']} ({apt_info['road_addr']}) "
          f"/ 대표좌표: {apt_info['lat']}, {apt_info['lng']} / danji_ids: {apt_info['danji_ids']}",
          file=sys.stderr)

    if apt_info["lat"] is None or apt_info["lng"] is None:
        raise RuntimeError("단지 좌표를 확인할 수 없습니다.")

    matched_rows = []
    for rings in range(1, max_rings + 1):
        geohashes = _geohashes_around(apt_info["lat"], apt_info["lng"], precision=6, rings=rings)
        markers = _fetch_markers(session, geohashes)
        details = _fetch_item_details(session, markers)

        matched_rows = []
        for mk in markers:
            it = details.get((mk["itemId"], mk["tradeType"]))
            if not it:
                continue
            if apt_info["danji_ids"] and it.get("areaDanjiId") not in apt_info["danji_ids"]:
                continue
            row = _to_row(mk, it)
            row["지번주소"] = apt_info["jibun_addr"]
            row["도로명주소"] = apt_info["road_addr"]
            matched_rows.append(row)

        print(f"rings={rings}: 마커 {len(markers)}건 중 이 단지 매물 {len(matched_rows)}건", file=sys.stderr)
        if matched_rows or not apt_info["danji_ids"]:
            break

    if out_csv:
        with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()
            writer.writerows(matched_rows)
        print(f"CSV 저장 완료: {out_csv}", file=sys.stderr)

    return matched_rows


if __name__ == "__main__":
    addr = sys.argv[1] if len(sys.argv) > 1 else "https://hogangnono.com/apt/6ipa0/item-catalog"
    out_csv = sys.argv[2] if len(sys.argv) > 2 else None
    items = get_hogangnono_items(addr, out_csv)
    print(json.dumps(items[:5], ensure_ascii=False, indent=2))
    