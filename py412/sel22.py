import pandas as pd

def sel22(dataset_name=None, *args):
    """
    데이터프레임에서 지정한 열(변수) 또는 범위만 선택하여 반환하는 함수.
    범위는 '시작컬럼명:끝컬럼명' 형태의 문자열로 입력합니다. (예: 'QA1:QA4')
    """
    # 1. 인자가 없을 경우 사용 예시 출력 (ANSI 색상 코드 적용)
    if dataset_name is None:
        print("\033[1;36m# 명령문 예제 ---------- \033[0m")
        print("\033[1;36m# df = pd.DataFrame({'A':[1], 'QA1':[2], 'QA2':[3], 'QA3':[4], 'B':[5]})\033[0m")
        print("\033[1;36m# df2 = sel22(df, 'A', 'QA1:QA3') \033[0m")
        print("\033[1;36m# print(df2) \033[0m")
        return None
    
    # 2. 선택할 변수가 입력되지 않은 경우 에러 발생
    if not args:
        raise ValueError("Error: Variables are not listed.")
        
    # 3. 데이터프레임 확인
    if not isinstance(dataset_name, pd.DataFrame):
        df = pd.DataFrame(dataset_name)
    else:
        df = dataset_name
        
    cols_to_select = []
    df_columns = list(df.columns)
    
    # 4. 선택할 변수명 추출 및 범위(':') 파싱
    for arg in args:
        if isinstance(arg, str) and ':' in arg:
            start_col, end_col = arg.split(':')
            start_col = start_col.strip()
            end_col = end_col.strip()
            
            # 두 컬럼이 모두 존재하는지 확인
            if start_col in df_columns and end_col in df_columns:
                start_idx = df_columns.index(start_col)
                end_idx = df_columns.index(end_col)
                
                # 정방향/역방향 슬라이싱 처리
                if start_idx <= end_idx:
                    cols_to_select.extend(df_columns[start_idx : end_idx + 1])
                else:
                    cols_to_select.extend(df_columns[end_idx : start_idx + 1])
            else:
                print(f"경고: 범위로 지정한 '{start_col}' 또는 '{end_col}' 컬럼이 존재하지 않습니다.")
        else:
            # 단일 컬럼일 경우
            if arg in df_columns:
                cols_to_select.append(arg)
            else:
                print(f"경고: '{arg}' 컬럼이 존재하지 않습니다.")
                
    # 5. 중복 제거 (리스트의 순서는 유지하기 위해 dict.fromkeys 활용)
    cols_to_select = list(dict.fromkeys(cols_to_select))
    
    # 6. 데이터 서브셋 생성 및 반환
    # 원본 데이터 보호를 위해 .copy() 사용 (R의 drop=FALSE는 판다스 DataFrame 반환으로 자연스럽게 해결됨)
    selected_dataset = df[cols_to_select].copy()
    
    return selected_dataset
