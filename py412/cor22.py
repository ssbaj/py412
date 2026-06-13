import pandas as pd
import numpy as np

# ---------------------------------------------------
# 1. 문자형 변수를 숫자형(Factor)으로 변환하는 독립 함수
# ---------------------------------------------------
def c2n(x=None):
    """문자열/범주형 데이터를 오름차순 정렬 후 1부터 시작하는 정수로 변환"""
    if x is None:
        print("  df['brandV2'] = c2n(df['brand'])")
        return None
    
    # 리스트나 배열이 들어올 경우 Series로 변환
    if not isinstance(x, pd.Series):
        x = pd.Series(x)
        
    # 결측치를 제외한 고유값을 추출하고 오름차순 정렬 (R의 sort(unique(x))와 동일)
    groups = sorted([val for val in x.unique() if pd.notna(val)])
    
    # 1부터 시작하는 정수로 매핑 딕셔너리 생성
    mapping = {val: i+1 for i, val in enumerate(groups)}
    
    # 변환된 값 반환
    return x.map(mapping)


# ---------------------------------------------------
# 2. 상관계수를 계산하는 함수 (내부에서 c2n 활용)
# ---------------------------------------------------
def cor22(x=None, y=None, digit=2):
    """
    상관계수를 계산하는 함수
    - x만 입력 시: 데이터프레임의 상관계수 행렬 반환 (상위 삼각은 빈칸 처리)
    - x, y 입력 시: 두 변수 간의 상관계수 반환
    """
    if x is None:
        print("   ")
        print("  \033[1;33mcor22(x, y, digit=4)\033[0m")
        print("  \033[1;33mcor22(df, digit=4)\033[0m")
        return None

    # CASE 1: 데이터셋 입력 모드 (y가 없을 때)
    if y is None:
        # 데이터프레임 변환 및 전처리
        if isinstance(x, pd.Series):
            df = x.to_frame()
        elif not isinstance(x, pd.DataFrame):
            df = pd.DataFrame(x)
        else:
            df = x.copy()

        # 문자형 변수인지 확인 후 외부의 c2n 함수 적용
        for col in df.columns:
            if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
                df[col] = c2n(df[col])

        # 수치형 변수만 선택
        df_numeric = df.select_dtypes(include=[np.number])

        # 상관계수 계산 및 반올림 (결측치는 자동 제외됨)
        res = df_numeric.corr().round(digit)

        # 상위 행렬 Blank 처리
        res_char = res.astype(object)
        mask = np.triu(np.ones(res.shape), k=1).astype(bool)
        res_char.mask(mask, "", inplace=True)
        res_char.fillna("", inplace=True)

        return res_char

    # CASE 2: 두 변수 입력 모드 (x, y가 있을 때)
    else:
        s_x = pd.Series(x).copy()
        s_y = pd.Series(y).copy()

        # 각 변수가 문자형인지 확인 후 c2n 적용
        if s_x.dtype == 'object' or pd.api.types.is_string_dtype(s_x):
            s_x = c2n(s_x)
        if s_y.dtype == 'object' or pd.api.types.is_string_dtype(s_y):
            s_y = c2n(s_y)

        # 결측치가 하나라도 있는 행 제거
        temp_df = pd.DataFrame({'x': s_x, 'y': s_y}).dropna()
        
        # 상관계수 계산
        corr_val = temp_df['x'].corr(temp_df['y'])
        
        return round(corr_val, digit)