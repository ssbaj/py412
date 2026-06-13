import pandas as pd
import statsmodels.formula.api as smf

def logit(formula=None, data=None, subset=None):
    # 1. 인자 없이 호출되었을 때 (사용 예시 출력)
    if formula is None or data is None:
        print("# ==========================================")
        print("# 사용 예시")
        print("# ==========================================")
        print("# 1. 라이브러리가 없다면 터미널에서 설치: pip install statsmodels")
        print("# 2. 결과 출력: ")
        print("# model_result = logit('survived ~ age + gender', df, 'age >= 2')")
        print("# print(model_result.summary())")
        return None

    # 2. subset을 적용한 데이터 생성
    if subset is not None:
        if isinstance(subset, str):
            # 문자열 조건식이 들어온 경우
            data_subset = data.query(subset)
        else:
            # 불리언 마스크가 들어온 경우
            data_subset = data[subset]
    else:
        # subset 조건이 없으면 원본 데이터 사용
        data_subset = data.copy()

    # 3. 로지스틱 회귀 모델 적합
    model = smf.logit(formula=formula, data=data_subset)
    re_logit = model.fit(disp=0) 
    
    return re_logit

