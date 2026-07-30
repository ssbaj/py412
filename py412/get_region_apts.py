"""
py412.get_region_apts
~~~~~~~~~~~~~~~~

호갱노노 지역 페이지에서 전체 단지 목록을 수집하는 모듈입니다.

[사용법 - CLI]
    1) python3 -m py412.get_region_apts "https://hogangnono.com/region/11680104/0"
    2) hgnn-danji "https://hogangnono.com/region/11680104/0" out.csv (console_script 등록 시)

[사용법 - Python]
    from py412.get_region_apts import get_region_apts
    
    # 1) 조회만 수행
    result = get_region_apts("https://hogangnono.com/region/11680111")

    # 2) 조회 및 CSV 저장
    result = get_region_apts("https://hogangnono.com/region/11680111", "tmp.csv")
"""

import csv
import json
import re
import sys
from typing import Dict, Any, Optional

from curl_cffi import requests as cffi_requests

API_URL_TEMPLATE = "https://hogangnono.com/api/region/{region_code}/apt"
REGION_URL_RE = re.compile(r"/region/(\d+)")
CSV_FIELDS = ["id", "name", "url", "address", "road_address", "total_household", "trade_count"]


def extract_region_code(region_url: str) -> str:
    m = REGION_URL_RE.search(region_url)
    if not m:
        raise ValueError(f"URL에서 지역코드를 찾을 수 없습니다: {region_url}")
    return m.group(1)


def to_long_region_code(region_code: str) -> str:
    return region_code.ljust(10, "0")


def save_to_json(result: Dict[str, Any], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)


def save_to_csv(result: Dict[str, Any], out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for apt in result["apts"]:
            writer.writerow({k: apt.get(k) for k in CSV_FIELDS})


def get_region_apts(
    region_url: str,
    out_path: Optional[str] = None,
    area_roughly: int = 0,
    timeout: int = 20,
) -> Dict[str, Any]:
    """지역 페이지 URL을 받아 단지 목록을 반환하며, 파일 경로 지정 시 저장합니다."""
    
    # 두 번째 인자로 정수가 들어온 경우 기존 area_roughly 매개변수로 하위 호환 처리
    if isinstance(out_path, int):
        area_roughly = out_path
        out_path = None

    region_code = extract_region_code(region_url)
    long_code = to_long_region_code(region_code)
    api_url = API_URL_TEMPLATE.format(region_code=long_code)

    resp = cffi_requests.get(
        api_url,
        params={"areaRoughly": area_roughly},
        impersonate="safari",
        headers={"Referer": region_url},
        timeout=timeout,
    )
    resp.raise_for_status()
    payload = resp.json()

    data = payload.get("data") or {}
    raw_apts = data.get("apts") or []

    apts = []
    for a in raw_apts:
        apt_id = a.get("id")
        apts.append({
            "id": apt_id,
            "name": a.get("name"),
            # URL 뒤에 /item-catalog 추가
            "url": f"https://hogangnono.com/apt/{apt_id}/item-catalog" if apt_id else "",
            "address": a.get("address"),
            "road_address": a.get("road_address"),
            "total_household": a.get("total_household"),
            "trade_count": a.get("trade_count"),
        })

    result = {
        "region_code": region_code,
        "long_region_code": long_code,
        "region_name": data.get("name"),
        "count": len(apts),
        "apts": apts,
    }

    # 파일 경로가 지정된 경우 확장자에 맞게 자동 저장
    if out_path:
        if out_path.lower().endswith(".csv"):
            save_to_csv(result, out_path)
        else:
            save_to_json(result, out_path)
        print(f"저장됨: {out_path}", file=sys.stderr)

    return result


def main() -> None:
    if len(sys.argv) < 2:
        print("사용법: python -m py412.hgnn_danji <region_url> [output.json|output.csv]", file=sys.stderr)
        sys.exit(1)

    region_url = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) >= 3 else None

    result = get_region_apts(region_url, out_path=out_path)

    print(f"{result['region_name']} ({result['region_code']}) - 총 {result['count']}개 단지")
    for apt in result["apts"]:
        print(f"  {apt['id']}\t{apt['name']}\t{apt['url']}")


if __name__ == "__main__":
    main()