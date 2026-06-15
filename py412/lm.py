import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

def lm(formula, data, subset=None):
    """
    R의 lm() 함수처럼 회귀분석, 결과 출력, 시뮬레이션 및 그래프 코드를 
    한 번에 실행해주는 사용자 정의 함수입니다.
    """
    # 1. 데이터 필터링 (subset 조건이 문자열로 주어졌을 때)
    if subset:
        df_filtered = data.query(subset)
    else:
        df_filtered = data.copy()
        
    # 2. 회귀분석 모형 실행
    model = smf.ols(formula=formula, data=df_filtered).fit()

    return(model)
