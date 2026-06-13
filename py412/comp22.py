import pandas as pd

def comp22(data=None, *cols):
    """
    결측치(NaN)가 포함된 행을 제거하는 함수
    - 변수를 지정하지 않으면 전체 컬럼 기준 결측치 제거
    - 변수를 지정하면 해당 컬럼들에 결측치가 있는 행만 제거
    """
    if data is None:
        print(" \033[1;36m# Examples ---------- \033[0m")
        print(" \033[1;36mdf = comp22(Adata, 'gender', 'debt') \033[0m")
        print(" \033[1;36mdf = comp22(Adata) \033[0m")
        return None

    # 원본 데이터 보호를 위해 복사본 사용
    cleaned_dataset = data.copy()

    # *cols를 통해 추가로 전달된 인자가 없는 경우 (R의 decision == 1)
    if not cols:
        cleaned_dataset = cleaned_dataset.dropna()
        
    # 추가로 전달된 변수명(인자)들이 있는 경우 (R의 decision == 0)
    else:
        cleaned_dataset = cleaned_dataset.dropna(subset=list(cols))

    return cleaned_dataset