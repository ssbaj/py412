import pandas as pd
import numpy as np


def mkgroup(name_dataset=None, select_columns=None, CuttingNumber=None, sign=1):
    # 1. 인자가 없을 경우 도움말 출력
    if name_dataset is None:
        print("\033[1;31m # ---------------------------------------------------------------------- \033[0m")
        print("\033[1;34m cn = df['income'].quantile([0.25, 0.5, 0.75]).tolist() \033[0m")
        print("\033[1;34m 또는, cn = [23.175, 45.700, 61.775] \033[0m")
        print("\033[1;31m # ---------------------------------------------------------------------- \033[0m")
        print("\033[1;34m df = mkgroup(df, 'income', cn) \033[0m")
        print("\033[1;34m 사용법: df, 컬럼명(문자열), 커팅넘버리스트, sign=1(미포함 <) \033[0m")
        print("\033[1;31m # ---------------------------------------------------------------------- \033[0m")
        print("\033[1;34m df = mkgroup(df, 'income', cn, 2) \033[0m")
        print("\033[1;34m 사용법: sign=2일 때, '포함 <=' 로 그룹화 \033[0m")
        print("\033[1;31m # ---------------------------------------------------------------------- \033[0m")
        return None

    # 데이터 복사본 생성
    df_result = name_dataset.copy()
    target_data = df_result[select_columns].values
   
    # NA 처리 알림
    if np.isnan(target_data).any():
        print(" ** Remove NAs ----")

    # 그룹화 로직 (Pandas의 pd.cut과 유사하게 작동)
    # R 코드의 루프 로직을 파이썬식으로 구현
    bins = sorted(CuttingNumber)
   
    if sign == 1:
        # 미포함 < (기본값)
        labels = list(range(1, len(bins) + 2))
        # bins = [20, 50] -> (-inf, 20), [20, 50), [50, inf)
        groups = pd.cut(target_data, bins=[-float('inf')] + bins + [float('inf')],
                        labels=labels, right=False)
    else:
        # 포함 <=
        labels = list(range(1, len(bins) + 2))
        groups = pd.cut(target_data, bins=[-float('inf')] + bins + [float('inf')],
                        labels=labels, right=True)

    # 결과 데이터프레임에 병합
    df_result[f'g_{select_columns}'] = groups.astype(int)
   
    return df_result
