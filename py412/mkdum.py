import pandas as pd
import numpy as np

def mkdum(name_dataset=None, select_columns=None):
    # 1. 인자가 누락되었을 때 도움말 예시 출력 (R의 base::missing 대조)
    if name_dataset is None or select_columns is None:
        print("    \033[1;36m# Examples ---------- \033[0m")
        print("    \033[1;36m Adata = pd.DataFrame(Adata) \033[0m")
        print("    \033[1;36m COMMAND: Adata = mkdum(Adata, 'variable') \033[0m")
        return None

    # 원본 데이터 복사 (원본 데이터 변형 방지)
    df = name_dataset.copy()
   
    # R과 달리 파이썬에서는 컬럼명을 문자열로 직접 입력받는 것이 안전합니다.
    if select_columns not in df.columns:
        raise ValueError(f"컬럼 '{select_columns}'이(가) 데이터프레임에 존재하지 않습니다.")
   
    # 2. 선택한 컬럼 추출 및 결측치 처리 (R의 tmp[is.na(tmp)] <- "NA" 대조)
    # 파이썬 고유의 NaN과 구별하기 위해 문자열 "NA"로 대체합니다.
    tmp_col = df[select_columns].astype(str).replace('nan', 'NA')
   
    # 고유값 개수 확인
    unique_elements = tmp_col.unique()
   
    # 3. 고유값이 2개뿐일 때의 처리
    if len(unique_elements) == 2:
        print(f" SUGGESTED COMMANDS: df['{select_columns}2'] = np.where(df['{select_columns}'] == '{unique_elements[0]}', 1, 0) ")
        return df
   
    # 4. 더미 변수 생성 (R의 model.matrix(~dum_ - 1, tmp) 대조)
    # R 코드의 네이밍 규칙(prefix_dum_값)을 그대로 재현합니다.
    dummies = pd.get_dummies(tmp_col, prefix=f"{select_columns}dum", dtype=int)
   
    # 5. 기존 데이터셋과 더미 변수 병합 (R의 cbind 대조)
    name_dataset2 = pd.concat([df, dummies], axis=1)
   
    return name_dataset2
