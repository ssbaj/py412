import pandas as pd
import numpy as np

# ---------------------------------------------------
# 1. 문자형 변수를 숫자형(Factor)으로 변환하는 독립 함수
# ---------------------------------------------------
def c2n(x=None):
    if x is None:
        print("  df['brandV2'] = c2n(df['brand'])")
        return None
    
    if not isinstance(x, pd.Series):
        x = pd.Series(x)
        
    groups = sorted([val for val in x.unique() if pd.notna(val)])
    mapping = {val: i+1 for i, val in enumerate(groups)}
    
    return x.map(mapping)


# ---------------------------------------------------
# 2. 특정 변수 기준 상관계수 계산 및 출력 함수
# ---------------------------------------------------
def cor33(dataframe=None, target_var=None):
    """
    특정 종속변수(target_var)와 다른 변수들 간의 상관계수를 계산하고,
    |상관계수|의 절대값이 큰 순서대로 내림차순 정렬하여 출력하는 함수
    """
    if dataframe is None or target_var is None:
        print("\033[1;32m## 상관계수 출력 -- \033[0m")
        print("\033[1;33m   cor33(df, '종속변수') \033[0m")  # 파이썬은 변수명에 따옴표 필수
        print("   출력 결과는 |상관계수|가 큰 값부터 보여줌 ")
        return None

    # 변수명 존재 여부 확인
    if target_var not in dataframe.columns:
        raise ValueError(f"에러: '{target_var}' 변수가 데이터프레임에 존재하지 않습니다.")

    # 데이터 전처리 (원본 보호를 위해 복사본 사용)
    df_proc = dataframe.copy()

    # 문자형/범주형 변수 숫자 변환 (c2n 적용)
    for col in df_proc.columns:
        if df_proc[col].dtype == 'object' or pd.api.types.is_string_dtype(df_proc[col]) or isinstance(df_proc[col].dtype, pd.CategoricalDtype):
            df_proc[col] = c2n(df_proc[col])

    # y변수(타겟 변수) 데이터 추출
    y_data = df_proc[target_var]
    
    # 결과를 저장할 리스트
    result_list = []

    # 상관계수 계산 루프
    for col in df_proc.columns:
        if col == target_var:
            continue
            
        x_data = df_proc[col]
        
        # NA 처리 (Pairwise complete): 두 변수 모두 결측치가 아닌 행만 추출
        valid_idx = x_data.notna() & y_data.notna()
        clean_x = x_data[valid_idx]
        clean_y = y_data[valid_idx]
        
        n_count = len(clean_x)
        
        # 데이터 2개 이상, 분산(표준편차) > 0 일 때 계산 (ddof=1은 R의 sd와 동일한 표본표준편차)
        if n_count >= 2 and clean_x.std(ddof=1) > 0 and clean_y.std(ddof=1) > 0:
            cor_val = clean_x.corr(clean_y)
            
            result_list.append({
                'name': col,
                'cor': cor_val,
                'n': n_count
            })

    if len(result_list) == 0:
        print("계산 가능한 상관계수가 없습니다.")
        return None

    # 리스트를 데이터프레임으로 변환
    res_df = pd.DataFrame(result_list)
    
    # 상관계수의 절대값(abs)을 기준으로 내림차순 정렬
    res_df['abs_cor'] = res_df['cor'].abs()
    res_df = res_df.sort_values(by='abs_cor', ascending=False).reset_index(drop=True)
    
    # 출력 포맷 생성 (R의 paste0 형태 구현)
    output_items = [f"{round(row['cor'], 3)}({row['name']}, {row['n']})" for _, row in res_df.iterrows()]

    # 결과 화면 출력
    print(f"dependent variable: {target_var}")
    print("(Sorted by Absolute Correlation Strength)")
    print("-" * 41)

    # 4개씩 탭(\t)으로 구분하여 출력
    for i, item in enumerate(output_items):
        print(item, end="\t")
        
        # 인덱스가 4의 배수일 때 줄바꿈 처리 (i는 0부터 시작하므로 i+1 기준)
        if (i + 1) % 4 == 0:
            print()
            
    # 마지막 줄이 4개로 딱 떨어지지 않았을 때 깔끔하게 줄바꿈 추가
    if len(output_items) % 4 != 0:
        print()