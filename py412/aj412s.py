def aj412s():
    guide_text = """
#------
from py412 import aj412s
import pandas as pd
import statsmodels.formula.api as smf

data = {
    'price': [250, 300, 350, 400, 450, 500],  # 종속변수: 집값 (단위: 천만 원)
    'size': [15, 20, 25, 30, 35, 40],         # 독립변수 1: 집 크기 (평수)
    'age': [10, 18, 5, 7, 2, 9]                # 독립변수 2: 연식 (지어진 지 몇 년?)
}

df = pd.DataFrame(data)

formula = 'price ~ size + age'

# ols(Ordinary Least Squares, 최소제곱법) 함수를 사용합니다.
model = smf.ols(formula=formula, data=df)
result = model.fit()
result = model.fit(cov_type='HC3')

HC0 : White (1980)
HC1자유도 조정 White 표준오차
HC3: 소규모 표본에 최적화된 표준오차. 표본 수가 적을 때 권장
HAC: Newey-West 표준오차. 이분산성뿐만 아니라 
     시계열 데이터의 자기상관(Autocorrelation)까지 통제할 때 사용
cluster: 군집 강건 표준오차 (Cluster-robust). 특정 그룹(패널 데이터 등)내의 상관관계를 통제


print(result.summary())


"""

    # 텍스트 앞뒤의 불필요한 공백/줄바꿈을 제거하고 출력합니다.
    print(guide_text.strip())
