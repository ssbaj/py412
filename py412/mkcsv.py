import pandas as pd
import warnings

def mkcsv(dataset=None, file_path=None, encoding='EUC-KR'):
    """
    데이터프레임을 CSV 파일로 저장하는 함수
    - 확장자가 생략된 경우 자동으로 .csv를 붙여줍니다.
    - 한글 깨짐을 방지하기 위해 기본 인코딩으로 EUC-KR을 사용합니다.
    """
    # 데이터셋이나 파일 경로가 입력되지 않은 경우 안내 메시지 출력
    if dataset is None or file_path is None:
        print("\033[1;32m# mkcsv(데이터셋, '새로운파일명.csv') \033[0m")
        print("\033[1;32m# csv파일 저장 디폴트: EUC-KR \033[0m")
        print("\033[1;32m# mkcsv(데이터셋, '새로운파일.csv', encoding='CP949') \033[0m")
        print("\033[1;32m# mkcsv(데이터셋, '새로운파일명.csv', encoding='UTF-8') \033[0m")
        print("\033[1;31m# 주의: 파이썬에서는 파일명에 반드시 따옴표를 사용하세요.\033[0m")
        return None

    # file_path를 문자열로 변환 (R의 deparse(substitute()) 대체)
    file_path = str(file_path)

    # 확장자 자동 보정 (.csv로 끝나지 않으면 추가, 대소문자 구분 없음)
    if not file_path.lower().endswith('.csv'):
        file_path += '.csv'

    # 지원되는 인코딩 목록 (파이썬 환경에 맞춰 소문자로 비교)
    # *참고: 파이썬에서 UTF-8 CSV를 엑셀로 열 때 한글이 깨진다면 'utf-8-sig'를 사용하면 좋습니다.
    supported_encodings = ['euc-kr', 'cp949', 'utf-8', 'utf-8-sig']

    # 입력받은 인코딩을 소문자로 변환하여 비교
    enc_lower = encoding.lower()

    if enc_lower not in supported_encodings:
        warnings.warn(f"지원되지 않는 인코딩입니다: '{encoding}'. 기본값 'EUC-KR'로 저장합니다.")
        enc_lower = 'euc-kr'

    # CSV 저장
    try:
        # index=False는 R의 row.names = FALSE와 완전히 동일한 기능입니다.
        dataset.to_csv(file_path, index=False, encoding=enc_lower)
        print(f"  CSV 저장 완료: '{file_path}'")
        
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {str(e)}")