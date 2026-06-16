import pandas as pd

def pipe22(df=None, *funcs, guide=""):
    # 가이드 출력 함수 내부 정의
    def print_guide():
        # 실행 결과 프린트 부분은 제외하고 예제 코드만 포함했습니다.
        guide_text = """
==================================================
 [pipe22 사용 예제 가이드]
==================================================
# 사용예 ---------------
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

print(df2)
=================================================="""
        print(guide_text)

    # 인자가 주어지지 않았을 때 가이드를 출력하고 함수 종료 (*funcs는 빈 튜플이 됨)
    if df is None and not funcs:
        print_guide()
        return
    
    # pipe22 본연의 기능 (함수 체이닝) 수행
    result = df
    for func in funcs:
        result = func(result)
    return result

# --- 테스트 실행 ---
# pipe22()
