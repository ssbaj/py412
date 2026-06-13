import pandas as pd

def mkxlsx(dataset=None, file_path=None):
    """
    데이터프레임을 엑셀 파일(.xlsx)로 저장하는 함수
    확장자가 생략된 경우 자동으로 .xlsx를 붙여줍니다.
    """
    # 데이터셋이나 파일 경로가 입력되지 않은 경우 안내 메시지 출력
    if dataset is None or file_path is None:
        print("\033[1;32m# 데이터셋을 엑셀 xlsx 파일로 저장하기 ----- \033[0m")
        print("\033[1;32m# mkxlsx(데이터셋, '새로운파일명.xlsx') \033[0m") # 파이썬은 따옴표 필수
        return None

    # file_path가 문자열인지 확인 (문자열 변환)
    file_path = str(file_path)

    # 확장자 자동 보정 (.xlsx로 끝나지 않으면 추가, 대소문자 구분 없음)
    if not file_path.lower().endswith('.xlsx'):
        file_path += '.xlsx'

    # xlsx 파일 저장
    try:
        # index=False는 R의 writexl처럼 행 번호를 출력하지 않도록 설정합니다
        dataset.to_excel(file_path, index=False, engine='openpyxl')
        print(f"  Excel 파일 저장 완료: '{file_path}'")
        
    except ModuleNotFoundError:
        # 파이썬에서 엑셀을 다루려면 openpyxl 패키지가 필요합니다
        print("에러: 엑셀 저장을 위해 'openpyxl' 패키지가 필요합니다.")
        print("터미널이나 셀에서 다음 명령어를 실행해주세요: pip install openpyxl")
        
    except Exception as e:
        print(f"파일 저장 중 오류가 발생함: {str(e)}")