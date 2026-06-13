def aj412s():
    """
    statsmodels 회귀분석 및 강건 표준오차(Robust Standard Error) 
    옵션에 대한 가이드 코드를 콘솔에 출력하는 함수입니다.
    """
    guide_text = """

from py412 import desc22, aj412s, comp22, files22, selvar
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

# df에서 v2, v3, v4 컬럼만 추출하여 새로운 데이터프레임 생성
newdf = df[['v2', 'v3', 'v4']].copy()

# newdf에서 v4 컬럼 제거 후 결과를 다시 newdf에 덮어쓰기
newdf = newdf.drop(columns=['v4'])

data = {
    'price': [250, 300, 350, 400, 450, 500],  # 종속변수: 집값 (단위: 천만 원)
    'size': [15, 20, 25, 30, 35, 40],         # 독립변수 1: 집 크기 (평수)
    'age': [10, 8, 5, np.nan, 2, 1]           # 독립변수 2: 연식 (지어진 지 몇 년?)
}

df = pd.DataFrame(data)

# ols(Ordinary Least Squares, 최소제곱법) 함수를 사용합니다.
result = smf.ols(formula='price ~ size + age', data=df).fit()
print(result.summary())

# Robust Standard Error를 사용하는 케이스
result = result.fit(cov_type='HC3')

1) HC0 : White (1980)
2) HC1자유도 조정 White 표준오차
3) HC3: 소규모 표본에 최적화된 표준오차. 표본 수가 적을 때 권장
4) HAC: Newey-West 표준오차. 이분산성뿐만 아니라 
        시계열 데이터의 자기상관(Autocorrelation)까지 통제할 때 사용
5) cluster: 군집 강건 표준오차 (Cluster-robust). 특정 그룹(패널 데이터 등)내의 상관관계를 통제


"""
    # 텍스트 앞뒤의 불필요한 공백/줄바꿈을 제거하고 출력합니다.
    print(guide_text.strip())