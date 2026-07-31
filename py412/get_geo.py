import requests

def get_geo(address, api_key):
    """
    'Shimbiro-5439f3d7eef2c504d3f7dad5c5d7a610'
    'ELCA-sVRAonkmHoaPlRc3bSQyM3elEka0GweK6KXSEPgm'
    """
    if not address or not api_key:
        print("[오류] 주소와 API 키를 모두 입력해주세요.")
        return None

    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status() # HTTP 오류 발생 시 예외 처리
        data = response.json()

        documents = data.get("documents", [])
        if not documents:
            print(f"[결과 없음] '{address}'에 대한 좌표를 찾을 수 없습니다.")
            return None

        # 카카오 API 응답 기준: x = 경도(Longitude), y = 위도(Latitude)
        lon = float(documents[0].get("x"))
        lat = float(documents[0].get("y"))

        return lat, lon

    except requests.exceptions.RequestException as e:
        print(f"[API 통신 오류] {e}")
        return None
