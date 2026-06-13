import pandas as pd

def recode(series=None, mapping=None, **kwargs):
    # 인자가 없으면 설명서 출력
    if series is None:
        print("    df['gpa'] = recode(df['gpa'], {1:'F', 2:'D', 3:'C', 4:'B', 5:'A' } ) # 문자열용")
        print("    df['gender'] = recode(df['gender'], {1:0, 2:1})  # 숫자/혼합용")
        return
    
    # 딕셔너리({ }) 형태로 입력이 들어온 경우 처리
    if mapping is not None:
        return series.replace(mapping)
    # 키워드(old1='new1') 형태로 입력이 들어온 경우 처리
    else:
        return series.replace(kwargs)
