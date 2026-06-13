import pandas as pd
import numpy as np

def desc22(data=None, digit=3):
    """
    모든 변수들의 요약 통계량(N, NAs, Zero, Mean, SD, Quantiles 등)을 계산하는 함수
    문자열/범주형 데이터는 알파벳 순서대로 1부터 시작하는 정수(Factor)로 자동 변환됩니다.
    """
    if data is None:
        print("  desc2(df) ")
        return None
    
    # 1. 입력 데이터를 DataFrame으로 안전하게 변환 및 복사 (원본 보호)
    if isinstance(data, pd.Series):
        df = data.to_frame()
    elif not isinstance(data, pd.DataFrame):
        df = pd.DataFrame(data, columns=['var'])
    else:
        df = data.copy()
        
    # 2. 문자열(Character) 변수를 R의 Factor(숫자)처럼 변환 (c2n 함수 역할)
    for col in df.columns:
        if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
            # 결측치를 제외한 고유값을 오름차순 정렬
            unique_vals = sorted([x for x in df[col].unique() if pd.notna(x)])
            # 1부터 시작하는 정수로 매핑 (R의 factor(levels=...)와 동일한 동작)
            mapping = {val: i+1 for i, val in enumerate(unique_vals)}
            df[col] = df[col].map(mapping)
            
    # 모든 변수를 강제로 숫자형으로 변환 (숫자로 바꿀 수 없는 예외 값은 NaN 처리)
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # 3. 기술 통계량 계산을 위한 빈 데이터프레임 생성 (행 이름은 기존 변수명)
    res = pd.DataFrame(index=df.columns)
    
    # 각 통계량 계산 (Pandas 함수들은 기본적으로 결측치(na.rm=True)를 무시하고 계산함)
    res['  Ndata'] = df.notna().sum()
    res['  NAs'] = df.isna().sum()
    res['  Zero'] = (df == 0).sum()
    # NaN이 아닌 값 중 0이 아닌 값을 카운트
    res['  nonzero'] = ((df != 0) & df.notna()).sum() 
    
    res['  Median'] = df.median()
    res['  Mean'] = df.mean()
    res['St.Dev.'] = df.std(ddof=1) # R과 동일한 표본표준편차 (n-1)
    res['Q1'] = df.quantile(0.25)
    res['Q2'] = df.quantile(0.50)
    res['Q3'] = df.quantile(0.75)
    res['  Min'] = df.min()
    res['  Max'] = df.max()
    res['  St.Dev/Mean'] = res['St.Dev.'] / res['  Mean']
    
    # 4. 지정한 소수점 자리수(digit)로 전체 반올림 적용
    res = res.round(digit)
    
    return res