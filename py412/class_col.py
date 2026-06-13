import pandas as pd

def class_col(data=None):
    # 인자가 없을 때 예시 출력 (R의 base::missing 대응)
    if data is None:
        print(" \033[1;36m# Examples ---------- \033[0m")
        print(" \033[1;36m  class_col(데이터셋) \033[0m")
        return

    # 데이터프레임으로 변환
    df = pd.DataFrame(data)
    
    print(" ")
    print("\033[1;31m # class of variables -------------------\033[0m ")
    
    # R처럼 1부터 시작하는 인덱스를 표현하기 위해 start=1 사용
    for i, col in enumerate(df.columns, start=1):
        dtype = df[col].dtype
        
        # 1. 숫자형 (R의 numeric 대응)
        if pd.api.types.is_numeric_dtype(dtype):
            print(f"    {col}({i}) \033[1;41m numeric  \033[0m")
            
        # 2. 문자형 (R의 character 대응)
        elif pd.api.types.is_string_dtype(dtype) or dtype == 'object':
            print(f"    {col}({i}) \033[1;34m character \033[0m")
            
        # 3. 범주형 (R의 factor 대응)
        elif isinstance(dtype, pd.CategoricalDtype):
            print(f"    {col}({i}) \033[1;35m factor    \033[0m")
            
        # 4. 그 외 기타 타입 (결과 직접 출력)
        else:
            print(f"    {col}({i}) {dtype}")
            
    print("\033[1;31m # --------------------------------------\033[0m ")
    print(" ")
