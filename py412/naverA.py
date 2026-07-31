"""
naverA: 네이버 부동산 매물 텍스트(txt, 여러 개) -> 엑셀 정리 함수
--------------------------------------------------------------
사용법:
1. pip install pandas openpyxl
2. naverA() 를 실행하면 파일 선택 팝업창이 뜬다.
3. 네이버 부동산 매물이 기록된 txt 파일
   (예: naver_copy.py 로 만든 my_copy202607301720.txt)을
   여러 개(2개 이상) 블록으로 선택하고 Enter 를 치면,
   선택한 모든 txt 파일의 내용을 하나로 합친 뒤 매물 정보를 정리해서
   "naver<생성시각>.xlsx" 로 저장한다. 이때 단지명/동/거래유형/
   보증금·매매가(만원)/평형코드 순으로 정렬한 뒤, 이 다섯 항목이 모두
   같은 매물은 중복으로 보고 1건만 남긴다.

전제 조건 (샘플 데이터 기준 텍스트 구조, 매물 1건당 아래 순서 반복):
    {단지명} {동}동
    {거래유형}{가격}                예) 매매19억 5,000 / 전세8억 8,000 / 월세2억/240
    {건물유형}{평형코드}/{전용면적}m², {현재층}/{총층}층, {방향}
    {특징 코멘트}                    (없을 수도 있음)
    {제공처} 제공
    {중개사무소명}
    확인매물 YY.MM.DD.  또는  등록일YY.MM.DD.
빈 줄은 모두 무시하고 처리한다. 일부 매물에는 "최근 변동 내역" 같은
가격 변동 이력이 거래유형과 면적 정보 사이에 끼어 들어가는데, 이런 매물은
면적 줄(m², 층 패턴)을 기준으로 다시 찾아 정렬하므로 자동으로 건너뛴다.
"""

import os
import re
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

import pandas as pd

_PRICE_RE = re.compile(r'^(?:(\d+)\s*억)?\s*([\d,]+)?$')
_DEAL_RE = re.compile(r'^(매매|전세|월세)(.+)$')
_DEAL_START_RE = re.compile(r'^(매매|전세|월세)')
_TYPE_RE = re.compile(r'^(\D+?)(\d+[A-Za-z]*)/(\d+)m²,\s*([^/,]+)/(\d+)층,\s*(\S+)$')
_TYPE_SEARCH_RE = re.compile(r'm²,.*층,')
_PROVIDER_END_RE = re.compile(r' 제공$')
_DATE_START_RE = re.compile(r'^(확인매물|등록일)')
_DATE_RE = re.compile(r'(확인매물|등록일)\s*(\d{2})\.(\d{2})\.(\d{2})')

_LOOKAHEAD = 6  # 거래유형 줄과 면적/층 줄 사이에 "최근 변동 내역" 같은 잡음이 끼어도 찾아내기 위한 탐색 폭

_OWNER_TAG_RE = re.compile(r'(집주인)+')  # 단지명 앞에 붙는 "집주인" 인증 표시 제거용


def _clean_complex_name(name):
    """단지명 앞에 붙은 '집주인' 표시(1개 이상 연속)를 제거한다."""
    if not name:
        return name
    return _OWNER_TAG_RE.sub('', name)


def _parse_price(text):
    """'19억 5,000' / '21억' / '2억' / '240' -> 만원 단위 정수"""
    text = text.strip()
    if not text:
        return None
    m = _PRICE_RE.match(text)
    if not m:
        return None
    eok = int(m.group(1)) if m.group(1) else 0
    man = int(m.group(2).replace(',', '')) if m.group(2) else 0
    return eok * 10000 + man


def _parse_deal_line(line):
    """'전세8억 8,000' / '매매19억 5,000' / '월세2억/240' -> (거래유형, 보증금/매매가, 월세)"""
    m = _DEAL_RE.match(line.strip())
    if not m:
        return None, None, None

    deal_type, rest = m.group(1), m.group(2).strip()
    if deal_type == "월세" and "/" in rest:
        deposit_text, rent_text = rest.split("/", 1)
        return deal_type, _parse_price(deposit_text), _parse_price(rent_text)

    return deal_type, _parse_price(rest), None


def _parse_type_line(line):
    """'아파트109C/83m², 10/15층, 남서향' -> dict"""
    m = _TYPE_RE.match(line.strip())
    if not m:
        return {"건물유형": None, "평형코드": None, "전용면적(m2)": None,
                "현재층": None, "총층": None, "방향": None}

    building, type_code, area, cur_floor, total_floor, direction = m.groups()
    return {
        "건물유형": building,
        "평형코드": type_code,
        "전용면적(m2)": int(area),
        "현재층": cur_floor,          # 숫자 문자열이거나 '저'/'중'/'고' 등
        "총층": int(total_floor),
        "방향": direction,
    }


def _parse_date_line(line):
    """'확인매물 26.07.30.' / '등록일26.07.01.' -> (구분, 'YYYY-MM-DD')"""
    m = _DATE_RE.search(line.strip())
    if not m:
        return None, None
    label, yy, mm, dd = m.groups()
    return label, f"20{yy}-{mm}-{dd}"


def _find_next_record_start(lines, i, n):
    """거래유형 줄(매매/전세/월세) 뒤 가까운 곳에서 면적/층 줄을 찾아
    (거래유형 줄 위치, 면적/층 줄 위치)를 반환한다. 둘 사이에 낀 줄(가격
    변동 이력 등)은 잡음으로 간주해 건너뛴다."""
    while i < n:
        if _DEAL_START_RE.match(lines[i]):
            for k in range(i + 1, min(i + 1 + _LOOKAHEAD, n)):
                if _TYPE_SEARCH_RE.search(lines[k]):
                    return i, k
        i += 1
    return None, None


def _parse_records(raw_text):
    lines = [ln.strip() for ln in raw_text.splitlines()]
    lines = [ln for ln in lines if ln]

    n = len(lines)
    records = []
    i = 0

    while True:
        deal_idx, type_idx = _find_next_record_start(lines, i, n)
        if deal_idx is None:
            break

        complex_line = lines[deal_idx - 1] if deal_idx - 1 >= 0 else None
        deal_line = lines[deal_idx]
        type_line = lines[type_idx]
        i = type_idx + 1

        comment = None
        if i < n and not _PROVIDER_END_RE.search(lines[i]):
            comment = lines[i]
            i += 1

        provider = None
        if i < n and _PROVIDER_END_RE.search(lines[i]):
            provider = lines[i]
            i += 1

        agent = None
        if i < n and not _DATE_START_RE.match(lines[i]):
            agent = lines[i]
            i += 1

        date_line = None
        if i < n and _DATE_START_RE.match(lines[i]):
            date_line = lines[i]
            i += 1

        if complex_line and " " in complex_line:
            complex_name, dong = complex_line.rsplit(" ", 1)
        else:
            complex_name, dong = complex_line, None

        complex_name = _clean_complex_name(complex_name)

        deal_type, price1, price2 = _parse_deal_line(deal_line)
        type_info = _parse_type_line(type_line)
        date_label, confirm_date = _parse_date_line(date_line) if date_line else (None, None)

        records.append({
            "단지명": complex_name,
            "동": dong,
            "거래유형": deal_type,
            "보증금/매매가(만원)": price1,
            "월세(만원)": price2,
            **type_info,
            "특징": comment,
            "제공처": provider.replace(" 제공", "").strip() if provider else None,
            "중개사무소": agent,
            "일자구분": date_label,
            "확인/등록일": confirm_date,
        })

    return records


def naverA():
    """
    실행하면 파일 선택 팝업이 뜨고, 네이버 부동산 매물이 기록된 txt 파일을
    여러 개(2개 이상) 선택 후 Enter 를 치면, 선택한 모든 파일의 내용을
    하나로 합쳐 매물 정보를 변수별로 정리한 뒤 "naver<생성시각>.xlsx"
    로 저장한다.
    """
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_paths = filedialog.askopenfilenames(
        title="네이버 부동산 매물 txt 파일 선택 (여러 개 선택 가능)",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
    )
    root.destroy()

    if not file_paths:
        print("파일이 선택되지 않았습니다.")
        return None

    raw_texts = []
    for path in file_paths:
        with open(path, "r", encoding="utf-8") as f:
            raw_texts.append(f.read())

    # 파일 사이 경계에서 앞뒤 매물이 서로 붙어버리지 않도록 빈 줄을 넣어 이어붙인다.
    combined_text = "\n\n".join(raw_texts)

    records = _parse_records(combined_text)
    if not records:
        messagebox.showwarning("naverA", "매물 데이터를 찾을 수 없습니다.")
        return None

    df = pd.DataFrame(records)

    dedup_cols = ["단지명", "동", "거래유형", "보증금/매매가(만원)", "평형코드"]
    df = df.sort_values(by=dedup_cols)

    before = len(df)
    df = df.drop_duplicates(subset=dedup_cols, keep="first")
    removed = before - len(df)
    if removed:
        print(f"[안내] 단지명/동/거래유형/보증금·매매가/평형코드가 같은 중복 매물 {removed}건을 제거했습니다.")

    out_dir = os.path.dirname(file_paths[0])
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    out_path = os.path.join(out_dir, f"naver{timestamp}.xlsx")
    df.to_excel(out_path, index=False)

    print(f"[완료] {len(file_paths)}개 파일을 합쳐 {out_path} 에 저장했습니다. (총 {len(df)}건)")

    return df


if __name__ == "__main__":
    naverA()
