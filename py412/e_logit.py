def e_logit():
    """
    콘솔에 logit 시뮬레이션 예제 코드 전체를 텍스트로 출력하는 함수입니다.
    """
    code_lines = r"""# ==========================================
# 1. 가상 데이터 생성 및 시뮬레이션 실행
# ==========================================
# 나이가 적을수록, 여성(gender=0)일수록 생존(survived=1) 확률이 높다고 가정한 가상 데이터
np.random.seed(42)
ages = np.random.randint(20, 60, 200)
genders = np.random.randint(0, 2, 200) # 0: 여성, 1: 남성

# 로짓 공식을 이용해 0과 1 사이의 확률 생성 후 이항 분포로 생존 여부 결정
z = 3.0 - 0.08 * ages - 1.5 * genders 
probs = np.exp(z) / (1 + np.exp(z))
survived = np.random.binomial(1, probs)

df = pd.DataFrame({'survived': survived, 'age': ages, 'gender': genders})

# ---------------------------------------------------------
# [기본 모형 실행] 작성하신 logit 함수 호출
# ---------------------------------------------------------
print("="*50)
print(" [로지스틱 회귀분석 결과]")
print("="*50)
model_result = logit(formula='survived ~ age + gender', data=df)
print(model_result.summary())
print("\n")

# ---------------------------------------------------------
# [시뮬레이션 1] age=30, gender=1(남성)일 때의 생존 확률 예측
# ---------------------------------------------------------
print("="*50)
print(" [시뮬레이션 1] 나이 30세, 남성(gender=1)의 생존 확률")
print("="*50)
sim1_data = pd.DataFrame({'age': [30], 'gender': [1]})
pred1 = model_result.predict(sim1_data)

# Logit의 예측값은 '확률'이므로 퍼센트(%)로 표현하면 이해하기 쉽습니다.
print(f"입력값: age = 30, gender = 1")
print(f"예측된 생존 확률: {pred1.iloc[0]:.2%} (약 {pred1.iloc[0]:.4f})\n")

# ---------------------------------------------------------
# [시뮬레이션 2] 나이 변화(20~60세), 여성(gender=0) 고정 시 확률 변화
# ---------------------------------------------------------
print("="*50)
print(" [시뮬레이션 2] 나이 변화에 따른 생존 확률 (여성 고정)")
print("="*50)
sim2_data = pd.DataFrame({
    'age': range(20, 65, 5), # 20세부터 60세까지 5살 간격
    'gender': [0] * 9          # 여성(0)으로 9개 행 고정
})

# 예측 결과를 데이터프레임의 새로운 열로 추가 (확률값)
sim2_data['pred_prob'] = model_result.predict(sim2_data)

print(sim2_data.to_string(index=False))
print("\n")

# ---------------------------------------------------------
# [그래프] 시뮬레이션 2 결과를 활용한 Logit Curve(S자 곡선) 그리기
# ---------------------------------------------------------
plt.figure(figsize=(7, 5))
plt.plot(sim2_data['age'], sim2_data['pred_prob'], 
         marker='o', linestyle='-', color='red', linewidth=2)

plt.title('Predicted Survival Probability by Age (Gender = 0)')
plt.xlabel('Age')
plt.ylabel('Survival Probability (0 to 1)')

# 로지스틱 회귀의 Y축은 확률이므로 0~1 사이로 고정해 주는 것이 좋습니다.
plt.ylim(-0.05, 1.05) 
plt.grid(True)
plt.show()"""

    print(code_lines)
