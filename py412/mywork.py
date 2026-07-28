def mywork():
    """
    statsmodels 회귀분석 및 강건 표준오차(Robust Standard Error) 
    옵션에 대한 가이드 코드를 콘솔에 출력하는 함수입니다.
    """
    guide_text = """
from py412 import class_col, comp22, cor22, cor33, del22, desc22, e_logit, files22, geocode_kakao, get_geo, lm, logit, mkcsv, mkdum, mkxlsx, mywork, recode, sel22, selvar, pipe22, filter22, select22, get_hogangnono_items
import py412 as py
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import inspect

# HogangNONO data ---------
addr="https://hogangnono.com/apt/6i404/item-catalog"
out="myfuntest.csv"
get_hogangnono_items(addr, out)

# 모듈 로드 후 inspect 실행
print(inspect.getsource(py.get_geo))
print(inspect.getsource(get_geo))

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
    lambda d: filter22(d, " (  var1 <= 17 ) "),    
    lambda d: select22(d, ['var2', 'var3'])
)

##----------------------------------------------------------------

# 모든 연습 문법(결측치, 텍스트 파싱, 그룹화, 회귀분석 등)을 커버하는 데이터셋
data = {
    'id': [f'EMP_{i:02d}' for i in range(1, 16)],
    'gender': ['M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M', 'F', 'M'],
    'age': [25, 30, 42, 28, 35, 50, np.nan, 22, 45, 31, 29, 38, 41, 27, 33],
    'v2': [10, 20, 15, 25, 30, 40, 12, 18, 35, 22, 28, 32, 38, 19, 24],
    'v3': [1.5, 2.3, 3.1, 1.8, 2.9, 4.0, 1.2, 1.1, 3.8, 2.1, 2.5, 3.3, 3.6, 1.9, 2.2],
    'v4': ['A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C', 'A', 'B', 'C'],
    'brand': [
        'KIA K5', 'HYUNDAI Avante', 'KIA Sorento', 'GENESIS G80', 'KIA Carnival',
        'BMW 520i', 'KIA Sportage', 'HYUNDAI Grandeur', 'KIA EV6', 'BENZ E-Class',
        'KIA Ray', 'HYUNDAI Tucson', 'KIA K8', 'VOLVO XC60', 'KIA Morning'
    ],
    '시군구': [
        '서울시 강남구', '서울시 서초구', '경기도 수원시', '서울시 송파구', '경기도 성남시',
        '서울시 마포구', '경기도 용인시', '서울시 종로구', '경기도 고양시', '서울시 영등포구',
        '경기도 부천시', '서울시 용산구', '경기도 안양시', '서울시 강동구', '경기도 화성시'
    ],
    '번지': [
        '01월 15일', '02월 03일', '10월 25일', '05월 08일', '11월 12일',
        '03월 01일', '07월 17일', '08월 15일', '09월 09일', '04월 05일',
        '06월 25일', '12월 31일', '01월 01일', '10월 09일', '05월 05일'
    ],
    'size': [15, 20, 25, 30, 35, 40, 18, 12, 38, 22, 21, 32, 33, 19, 24],
    'price': [250, 300, 350, 400, 450, 500, 280, 220, 480, 320, 310, 420, 430, 290, 340]
}

df = pd.DataFrame(data)

# 데이터셋 미리보기
print(df.head())

##----------------------------------------------------------------

# 📈 데이터 마이닝 ----------
# Grouping variable
cn = df['age'].quantile([0.25, 0.5, 0.75])
df['age_group'] = pd.cut(df['age'], bins=[-np.inf, cn[0.25], cn[0.5], cn[0.75], np.inf])

# Aggregate examples
agg1 = df.groupby('gender')['age'].mean()
agg2 = df.groupby('gender')['age'].agg(['count', 'mean', 'std'])

# df에서 v2, v3, v4 컬럼만 추출하여 새로운 데이터프레임 생성
newdf = sel22(df, 'v2:v4')
newdf = df[['v2', 'v3', 'v4']].copy()

# 변수명 바꾸기 janitor --------------
import janitor # 설치 후 불러오기만 하면 pandas 메서드로 자동 등록됩니다.

# 샘플 데이터
df_janitor = pd.DataFrame({
    'First Name': ['Kim', 'Lee'],
    'AGE (year)': [25, 30],
    'v1': [10, 20]
})

# 1) clean_names(): 공백, 특수문자, 대문자를 자동으로 소문자_언더바 형태로 일괄 정리
df_clean = df_janitor.clean_names()

# 2) rename_columns(): 딕셔너리로 간편하게 변경 (메서드 체이닝 가능)
df_renamed = df_janitor.rename_columns({'First Name': 'name', 'AGE (year)': 'age'})

# 3) 위치(인덱스) 기반으로 손쉽게 변경
df_pos = df_janitor.rename_columns({df_janitor.columns[0]: 'id', df_janitor.columns[1]: 'age'})

# filter 명령문 --------------
df = df[df['brand'].str.contains('KIA')].copy()

# df에서 v4 컬럼 제거 후 결과를 다시 df에 덮어쓰기
df = del22(df, 'v4')
df = df.drop(columns=['v4'], errors='ignore')

# 번지 만들기 --------------
df['번지'] = df['번지'].str.replace(r'0?([0-9]+)월 0?([0-9]+)일', r'\1 - \2', regex=True)
df['addr'] = df['시군구'] + ' ' + df['번지']

# Drop missing values (complete.cases)
df = df.dropna()
df = df.dropna(subset=['age', 'gender'])

# Change column types -------
cols = ['age', 'gender']
df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')

# Count NA ------
na_count = df['age'].isna().sum()

# 📈 pivot - wide 데이터 마이닝 ----------
data_pivot = {
    'id': [f'EMP_{i:02d}' for i in range(1, 5)],
    'HR': [25, 30, 42, 28],
    'IT': [27, 32, 40, 29]
}

df_pivot = pd.DataFrame(data_pivot)

# melt 명령어 적용
df_long = df_pivot.melt(id_vars=['id'], var_name='dept', value_name='age')

# 두 데이터프레임 비교 출력
print("================ [1] 원본 데이터 (df - Wide Format) ================")
print(df_pivot)
print("============ [2] 변환된 데이터 (df_long - Long Format) ============")
print(df_long)

# Pivot wider
df_wide = df_long.pivot_table(index='id', columns='dept', values='age', aggfunc='first').reset_index()

# 📈 회귀분석 ----------
reg_data = {
    'price': [250, 300, 350, 400, 450, 500],
    'size': [15, 20, 25, 30, 35, 40],
    'age': [10, 8, 5, np.nan, 2, 1]
}

df_reg = pd.DataFrame(reg_data)

# lm 함수 예시
result = lm('price ~ size + age', data=df_reg)

# statsmodels 예시
model = smf.ols(formula='price ~ size + age', data=df_reg)
result = model.fit()
print(result.summary())

# Robust Standard Error를 사용하는 케이스
result_hc3 = model.fit(cov_type='HC3')

# 1) HC0 : White (1980)
# 2) HC1 : 자유도 조정 White 표준오차
# 3) HC3 : 소규모 표본에 최적화된 표준오차. 표본 수가 적을 때 권장
# 4) HAC : Newey-West 표준오차. 이분산성뿐만 아니라 시계열 데이터의 자기상관 통제
# 5) cluster : 군집 강건 표준오차 (Cluster-robust). 특정 그룹 내 상관관계 통제

# 📈 시뮬레이션 1 ----------
sim1_data = pd.DataFrame({'size': [3], 'age': [3]})
pred1 = result.predict(sim1_data)
print(f"예측된 price: {pred1.iloc[0]:.4f}\\n")

# 📈 시뮬레이션 2 ----------
sim2_data = pd.DataFrame({
    'size': [1, 2, 3],
    'age': [3, 3, 3]
})

sim2_data['predicted_price'] = result.predict(sim2_data)
print(sim2_data.to_string(index=False))

# 📈 시뮬레이션 2를 활용한 Line Graph 설명문 ----------
import matplotlib.pyplot as plt
plt.figure(figsize=(6, 4))
plt.plot(sim2_data['size'], sim2_data['predicted_price'], 
         marker='o', linestyle='-', color='blue')
plt.title('Predicted Price by Size (Fixed Age = 3)')
plt.xlabel('Size')
plt.ylabel('Predicted Price')
plt.xticks([1, 2, 3])
plt.grid(True)
plt.show()
"""
    print(guide_text.strip())
