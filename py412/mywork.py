def mywork():
    """
    statsmodels 회귀분석 및 강건 표준오차(Robust Standard Error) 
    옵션에 대한 가이드 코드를 콘솔에 출력하는 함수입니다.
    """
    guide_text = """

#  📈 데이터 마이닝 ----------
# df에서 v2, v3, v4 컬럼만 추출하여 새로운 데이터프레임 생성
 newdf = df[['v2', 'v3', 'v4']].copy()

# newdf에서 v4 컬럼 제거 후 결과를 다시 newdf에 덮어쓰기
 newdf = newdf.drop(columns=['v4'])

# 번지 만들기
 df['번지'] = df['번지'].str.replace(r'0?([0-9]+)월 0?([0-9]+)일', r'\1-\2', regex=True)
 df['addr'] = df['시군구'] + ' ' + df['번지']

#  📈 회귀분석 ----------
from py412 import desc22, aj412s, comp22, files22, selvar, lm
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

data = {
    'price': [250, 300, 350, 400, 450, 500],  # 종속변수: 집값 (단위: 천만 원)
    'size': [15, 20, 25, 30, 35, 40],         # 독립변수 1: 집 크기 (평수)
    'age': [10, 8, 5, np.nan, 2, 1]           # 독립변수 2: 연식 (지어진 지 몇 년?)
}

df = pd.DataFrame(data)

# ols(Ordinary Least Squares, 최소제곱법) 함수를 사용합니다.
result = lm('price ~ size + age', data=df)
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


#  📈 시뮬레이션 1 ----------

sim1_data = pd.DataFrame({'size': [3], 'age': [3]})
pred1 = model.predict(sim1_data)
print(f"예측된 price: {pred1.iloc[0]:.4f}\n")

#  📈 시뮬레이션 2 ----------
sim2_data = pd.DataFrame({
    'size': [1, 2, 3],
    'age': [3, 3, 3]
})

sim2_data['predicted_price'] = model.predict(sim2_data)
print(sim2_data.to_string(index=False))

#  📈 시뮬레이션 2를 활용한 Line Graph 설명문 ----------
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.plot(sim2_data['size'], sim2_data['predicted_price'], 
         marker='o', linestyle='-', color='blue')
plt.title('Predicted Price by Size (Fixed Age = 3)')
plt.xlabel('Size')
plt.ylabel('Predicted Price')
plt.xticks([1, 2, 3]) # X축 눈금 고정
plt.grid(True)
plt.show()

"""
    # 텍스트 앞뒤의 불필요한 공백/줄바꿈을 제거하고 출력합니다.
    print(guide_text.strip())