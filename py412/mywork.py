def mywork():
    """
    statsmodels 회귀분석 및 강건 표준오차(Robust Standard Error) 
    옵션에 대한 가이드 코드를 콘솔에 출력하는 함수입니다.
    """
    guide_text = """

from py412 import class_col, comp22, cor22, cor33, del22, desc22, e_logit, files22, geocode_kakao, lm, logit, mkcsv, mkdum, mkxlsx, mywork, recode, sel22, selvar

import statsmodels.formula.api as smf

import py412 as py

# pipe22, filter22, select22 사용예 ---------------
df = pd.DataFrame({
    'var1': [11, 12, 13, 14, 15, 16, 17, 18],
    'var2': [10, 20, 30, 40, 50, 60, 70, 80],
    'var3': [111, 112, 113, 114, 115, 116, 117, 118]
})

# R 스타일: df %>% filter(...) %>% select(...)
# 파이썬 함수 스타일:
df2 = pipe22(
    df,
    lambda d: filter22(d, " ( (var2!=30)  and (var3 != 114) ) "),
    lambda d: filter22(d, " (  var1 <= 17 ) ") ,    
    lambda d: select22(d, ['var2', 'var3'])
)


#  📈 데이터 마이닝 ----------
# Grouping variable
cn = df['age'].quantile([0.25,0.5,0.75])
df['age_group'] = pd.cut(df['age'], bins=[-np.inf,cn[0.25],cn[0.5],cn[0.75],np.inf])

# Aggregate examples
agg1 = df.groupby('gender')['age'].mean()
agg2 = df.groupby('gender')['age'].agg(['count','mean','std'])

# df에서 v2, v3, v4 컬럼만 추출하여 새로운 데이터프레임 생성
 newdf = sel22(df, 'v2:v4')
 newdf = df[['v2', 'v3', 'v4']].copy()

# rename
 df.columns = ['id2', 'conv2', 'brand2']

# filter 명령문
 df = df[df['brand'].str.contains('KIA')].copy()

# df에서 v4 컬럼 제거 후 결과를 다시 df에 덮어쓰기
 df = del22(df, 'v4')
 df = df.drop(columns=['v4'])

# 번지 만들기
 df['번지'] = df['번지'].str.replace(r'0?([0-9]+)월 0?([0-9]+)일', r'\1-\2', regex=True)
 df['addr'] = df['시군구'] + ' ' + df['번지']

# Drop missing values (complete.cases)
df = df.dropna()
df = df.dropna(subset=['age','gender'])

# Change column types -------
cols = ['age','gender']
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

# Count NA ------
na_count = df['age'].isna().sum()

#  📈 pivot - wide 데이터 마이닝 ----------
import pandas as pd
# A1. 10개의 자료로 구성된 원본 데이터프레임(df) 생성
# 사원 ID별로 'HR(인사부)'과 'IT(전산부)' 부서에 근무했을 당시의 나이(가상 데이터)

data = {
    'id': [f'EMP_{i:02d}' for i in range(1, 5)],
    'HR': [25, 30, 42, 28],
    'IT': [27, 32, 40, 29]
    }

df = pd.DataFrame(data)

# A2. melt 명령어 적용
df_long = df.melt(id_vars=['id'], var_name='dept', value_name='age')

# A3. 두 데이터프레임 비교 출력
print("================ [1] 원본 데이터 (df - Wide Format) ================")
print(df)
print("============ [2] 변환된 데이터 (df_long - Long Format) ============")
print(df_long)

# Pivot wider (tidyr pivot_wider)
df_wide = df_long.pivot_table(index='id', columns='dept', values='age', aggfunc='first').reset_index()

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