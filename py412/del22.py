import pandas as pd

def del22(dataset_name=None, *args):
    """
    데이터프레임에서 지정한 열(변수) 또는 범위를 삭제하여 반환하는 함수.
    범위는 '시작컬럼명:끝컬럼명' 형태의 문자열로 입력합니다. (예: 'QA1:QA4')
    """
    # 1. 인자가 없을 경우 사용 예시 출력
    if dataset_name is None:
        print("# === 사용 예시 ===")
        print("# df = pd.DataFrame({'A':[1], 'QA1':[2], 'QA2':[3], 'QA3':[4], 'QA4':[5], 'B':[6]})")
        print("# df2 = del22(df, 'QA1:QA4', 'B')")
        print("# print(df2)")
        return None
    
    # 2. 데이터프레임으로 변환 및 복사
    if not isinstance(dataset_name, pd.DataFrame):
        df = pd.DataFrame(dataset_name)
    else:
        df = dataset_name.copy()
        
    # 3. 삭제할 변수명 추출 로직 (범위 파싱 추가)
    cols_to_drop = []
    df_columns = list(df.columns)
    
    for arg in args:
        # 인자에 콜론(':')이 포함된 문자열인 경우 범위로 인식
        if isinstance(arg, str) and ':' in arg:
            start_col, end_col = arg.split(':')
            start_col = start_col.strip()
            end_col = end_col.strip()
            
            # 두 컬럼이 데이터프레임에 모두 존재하는지 확인 후 인덱스 추출
            if start_col in df_columns and end_col in df_columns:
                start_idx = df_columns.index(start_col)
                end_idx = df_columns.index(end_col)
                
                # 시작 인덱스와 끝 인덱스 순서에 상관없이 정상적으로 슬라이싱되도록 처리
                if start_idx <= end_idx:
                    cols_to_drop.extend(df_columns[start_idx : end_idx + 1])
                else:
                    cols_to_drop.extend(df_columns[end_idx : start_idx + 1])
            else:
                print(f"경고: 범위로 지정한 '{start_col}' 또는 '{end_col}' 컬럼이 존재하지 않습니다.")
        else:
            # 일반 단일 컬럼명인 경우
            cols_to_drop.append(arg)
            
    # 중복 제거 (동일한 컬럼이 여러 번 지정될 경우를 대비)
    cols_to_drop = list(set(cols_to_drop))
    
    # 4. 데이터 정제: 추출된 컬럼 일괄 삭제
    clean_data = df.drop(columns=cols_to_drop, errors='ignore')
    
    return clean_data
