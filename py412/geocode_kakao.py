import requests

def geocode_kakao(REST_API_KEY=None, address=None):
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
    
    Examples
    --------
    my_kakao_rest = 'your-kakao-rest-api-key'
    addr = '경기도 수원시 영통구 원천동 산5-1'
    result = geocode_kakao(my_kakao_rest, addr)
    print(result)  # [위도, 경도]
    """

    # REST_API_KEY 없으면 사용법 출력
    if REST_API_KEY is None:
        print("""
 필요 라이브러리: requests, pandas
 pip install requests pandas

 # 국토정보플랫폼     : https://map.ngii.go.kr/
 # 환경공간정보서비스 : https://egis.me.go.kr/
 # 실거래가공개시스템 : https://rt.molit.go.kr/
 # KB통계            : https://kbland.kr/
 # 콤파스            : https://compas.lh.or.kr/

 -----------------------------------------------
 사용 예시:

 from py412 import geocode_kakao, files22
 import pandas as pd

 my_kakao_rest = 'your-kakao-rest-api-key'

 df = files22()
 df = pd.DataFrame(df)

 # 지번 패턴 변환 (0x월 0x일 -> x-x)
 import re
 df['jibun'] = df['jibun'].str.replace(r'0?([0-9]+)월 0?([0-9]+)일', r'\\1-\\2', regex=True)

 # 특정 지역 필터링
 newdf = df[df['bjd_nm'].str.contains('경기도 성남시 중원구 상대원동')].copy()
 newdf['addr'] = newdf['bjd_nm'] + ' ' + newdf['jibun']

 newdf['lat_y'] = None
 newdf['long_x'] = None

 for i, row in newdf.iterrows():
     addr = row['addr']
     try:
         longlat = geocode_kakao(my_kakao_rest, addr)
         if longlat and len(longlat) >= 2:
             newdf.at[i, 'lat_y'] = longlat[0]
             newdf.at[i, 'long_x'] = longlat[1]
             print(longlat, i, ': 번째')
     except Exception as e:
         newdf.at[i, 'lat_y'] = None
         newdf.at[i, 'long_x'] = None

 newdf.to_csv('newdf.csv', index=False, encoding='utf-8-sig')
 -----------------------------------------------
        """)
        return None

    # 주소 없으면 종료
    if address is None:
        print("[오류] address 인자가 필요합니다.")
        return None

    # 주소가 리스트면 첫 번째 값만 사용 (R의 address[1] 동일)
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

        lat_x = documents[0].get("x")  # 경도
        long_y = documents[0].get("y")  # 위도

        return [lat_x, long_y]

    except requests.exceptions.RequestException as e:
        print(f"[API 오류] {e}")
        return None