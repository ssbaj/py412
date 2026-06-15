import requests
import time


def geocode_df(REST_API_KEY=None, address=None):
    """
    카카오 REST API를 이용한 주소 -> 위경도 변환 함수
    
    Parameters
    ----------
    REST_API_KEY : str
        카카오 REST API 키
    address : str
        지번 주소 또는 도로명 주소
    
    Returns
    -------
    list : [위도(y), 경도(x)] 또는 None
    """
    if REST_API_KEY is None:
        print("""
 필요 라이브러리: requests, pandas
   # pip install requests pandas

 # 국토정보플랫폼     : https://map.ngii.go.kr/
 # 환경공간정보서비스 : https://egis.me.go.kr/
 # 실거래가공개시스템 : https://rt.molit.go.kr/
 # KB통계            : https://kbland.kr/
 # 콤파스            : https://compas.lh.or.kr/

 -----------------------------------------------
 사용 예시:

 from geocode_kakao import geocode_df, geocode_kakao
 import pandas as pd

 my_kakao_rest = 'YOUR_KAKAO_REST_API_KEY'

 df = pd.read_csv('YOUR_DATA_SET.csv')
 df = pd.read_excel('파일명.xlsx')
 # df 에는 반드시 'addr' 컬럼이 있어야 합니다.

 result_df = geocode_kakao(my_kakao_rest, df)
 result_df.to_csv('result.csv', index=False, encoding='utf-8-sig')
 -----------------------------------------------
        """)
        return None

    if address is None:
        print("[오류] address 인자가 필요합니다.")
        return None

    if isinstance(address, list):
        address = address[0]

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {REST_API_KEY}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        documents = data.get("documents", [])
        if not documents:
            print(f"[결과 없음] 주소를 찾을 수 없습니다: {address}")
            return None

        long_x = documents[0].get("x")  # 경도
        lat_y = documents[0].get("y")   # 위도

        return [long_x, lat_y]

    except requests.exceptions.RequestException as e:
        print(f"[API 오류] {e}")
        return None


def geocode_kakao(REST_API_KEY=None, df=None, addr_col="addr", delay=0.1):
    """
    데이터프레임의 주소 컬럼을 일괄 지오코딩하여 lat_y, long_x 컬럼을 추가하는 함수

    Parameters
    ----------
    REST_API_KEY : str
        카카오 REST API 키
    df : pandas.DataFrame
        주소 컬럼(addr_col)이 포함된 데이터프레임
    addr_col : str, optional
        주소가 담긴 컬럼명 (기본값: 'addr')
    delay : float, optional
        API 호출 간 대기 시간(초). 기본값 0.1초 (과호출 방지)

    Returns
    -------
    pandas.DataFrame
        lat_y(위도), long_x(경도) 컬럼이 추가된 데이터프레임

    Examples
    --------
    사용 예시:

        from geocode_kakao import geocode_kakao
        import pandas as pd

        my_kakao_rest = 'YOUR_KAKAO_REST_API_KEY'

        df = pd.read_csv('your_data.csv')
        df = pd.read_excel('파일명.xlsx')
        # df 에는 반드시 'addr' 컬럼이 있어야 합니다.
        # 컬럼명이 다를 경우: geocode_kakao(key, df, addr_col='주소컬럼명')

        result_df = geocode_kakao(my_kakao_rest, df)
        print(result_df[['addr', 'lat_y', 'long_x']])

        result_df.to_csv('result.csv', index=False, encoding='utf-8-sig')
    """

    # ── 인자 없이 호출 시 사용법 출력 ──────────────────────────────────────────
    if REST_API_KEY is None:
        print("""
 ┌─────────────────────────────────────────────────────────────┐
 │              geocode_kakao() 사용법                            │
 └─────────────────────────────────────────────────────────────┘

 필요 라이브러리: requests, pandas
   # pip install requests pandas

 ── 기본 사용법 ──────────────────────────────────────────────

 from py412 import geocode_kakao
 import pandas as pd

 my_kakao_rest = 'YOUR_KAKAO_REST_API_KEY'   # 카카오 REST API 키
 df = pd.read_excel('YOUR_DATA_SET.xlsx')    # 데이터셋이 xlsx파일인 경우. addr 컬럼 포함 필수
 df = pd.read_csv('YOUR_DATA_SET.csv')       # 데이터셋이 csv파일인 경우. addr 컬럼 포함 필수
 
 result_df = geocode_kakao(my_kakao_rest, df)
 result_df.to_csv('result.csv', index=False, encoding='utf-8-sig')

 ── 주소 만들기 ──────────────────────────────
 # 지번 패턴 변환 (0x월 0x일 -> x-x)
 import re
 df['번지'] = df['번지'].str.replace(r'0?([0-9]+)월 0?([0-9]+)일', r'\\1-\\2', regex=True)
 df['addr'] = df['시군구'] + ' ' + newdf['번지']

 # 특정 지역 필터링
 newdf = df[df['시군구'].str.contains('경기도 성남시 중원구 상대원동')].copy()
 
 ── 컬럼명이 'addr'이 아닐 경우 ──────────────────────────────
 result_df = geocode_kakao(my_kakao_rest, df, addr_col='주소')

 ── API 호출 간격 조정 (기본 0.1초) ──────────────────────────

 result_df = geocode_kakao(my_kakao_rest, df, delay=0.3)

 ── 반환값 ───────────────────────────────────────────────────
 lat_y  : 위도 (y좌표)
 long_x : 경도 (x좌표)
 좌표를 찾지 못한 행은 None으로 채워집니다.

 ── 카카오 REST API 키 발급 ──────────────────────────────────

 https://developers.kakao.com/ 에서 애플리케이션 생성 후
 [앱 키] > [REST API 키] 사용

 ── 참고 데이터 출처 ─────────────────────────────────────────

 # 국토정보플랫폼     : https://map.ngii.go.kr/
 # 환경공간정보서비스 : https://egis.me.go.kr/
 # 실거래가공개시스템 : https://rt.molit.go.kr/
 # KB통계            : https://kbland.kr/
 # 콤파스            : https://compas.lh.or.kr/
        """)
        return None

    # ── 데이터프레임 없으면 종료 ───────────────────────────────────────────────
    if df is None:
        print("[오류] df 인자가 필요합니다. 데이터프레임을 전달하세요.")
        return None

    # ── addr 컬럼 존재 확인 ────────────────────────────────────────────────────
    if addr_col not in df.columns:
        print(f"[오류] 데이터프레임에 '{addr_col}' 컬럼이 없습니다.")
        print(f"       현재 컬럼 목록: {list(df.columns)}")
        print(f"       addr_col 인자로 올바른 컬럼명을 지정하세요.")
        return None

    result = df.copy()
    result["lat_y"] = None
    result["long_x"] = None

    total = len(result)
    success = 0
    fail = 0

    print(f"[시작] 총 {total}개 주소 지오코딩을 시작합니다...\n")

    for i, (idx, row) in enumerate(result.iterrows(), start=1):
        addr = row[addr_col]

        # 주소가 비어있으면 스킵
        if not addr or (isinstance(addr, float)):
            print(f"  [{i:>5}/{total}] 건너뜀 (주소 없음) — 인덱스 {idx}")
            fail += 1
            continue

        try:
            coords = geocode_df(REST_API_KEY, addr)

            if coords and len(coords) >= 2:
                result.at[idx, "long_x"] = coords[0]
                result.at[idx, "lat_y"] = coords[1]
                print(f"  [{i:>5}/{total}] ✔ ({coords[1]}, {coords[0]})  ← {addr}")
                success += 1
            else:
                print(f"  [{i:>5}/{total}] ✘ 좌표 없음  ← {addr}")
                fail += 1

        except Exception as e:
            print(f"  [{i:>5}/{total}] ✘ 오류: {e}  ← {addr}")
            fail += 1

        # API 과호출 방지 대기
        if delay > 0:
            time.sleep(delay)

    print(f"""
[완료] 지오코딩 결과
  - 전체  : {total}건
  - 성공  : {success}건
  - 실패  : {fail}건
    """)

    return result

