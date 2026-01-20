# 📂 PJ04_Secure_OOP_Portfolio

**(부제: 객체지향 프로그래밍으로 구축한 안전하고 확장 가능한 주식 거래 시스템)**

> **"변수는 숨기고, 기능은 물려받는다."** > 기존의 함수형(Functional) 코드가 가진 보안 취약점과 확장성 문제를 해결하기 위해, **Python Class(객체지향)** 기반으로 리팩터링한 자산 관리 시스템입니다.

---

## 1. 프로젝트 개요 (Overview)

* **프로젝트 명:** PJ04_Secure_OOP_Portfolio
* **수행 기간:** 2026.01.16~20 (5일)
* **목표:** 
1. 전역 변수 사용으로 인한 **데이터 오염 방지 (Encapsulation)**
2. 고객 등급(일반/VIP)에 따른 **기능 확장성 확보 (Inheritance)**
3. 실제 주식 시장의 **매수(이동평균법)/매도(실현손익)** 로직 구현

## 2. 핵심 기술 및 구현 기능 (Key Features)

### 🔒 1. 캡슐화 (Encapsulation) - 보안 강화

* **문제:** 기존 코드에서는 외부에서 `balance` 변수에 직접 접근해 잔고를 조작할 수 있었음.
* **해결:** - `self.__balance` (Private Variable)를 사용하여 외부 접근을 원천 차단.
* `get_balance()` (Getter) 메서드를 통해서만 잔고를 조회할 수 있도록 '읽기 전용' 권한 부여.
* `deposit()` 메서드를 통해서만 잔고 수정이 가능하도록 로직 통제.



### 🧬 2. 상속 (Inheritance) - 확장성 확보

* **문제:** VIP 고객을 위한 수수료 우대 기능을 추가하려면 기존 코드를 복사-붙여넣기 해야 하는 비효율 발생.
* **해결:**
* `Portfolio` 클래스를 상속받는 `VIPPortfolio` 클래스 정의.
* **Overriding:** `buy`, `sell` 로직은 그대로 물려받되, `commission_rate`만 `0.0`으로 재정의하여 코드 중복 없이 기능 확장.



### 📈 3. 트레이딩 로직 (Trading Logic)

* **클래스 변수:** `commission_rate`를 클래스 변수로 선언하여 모든 인스턴스의 수수료율을 일괄 관리.
* **매수 (이동평균법):** 추가 매수 시 기존 보유 수량과 평단가를 고려하여 새로운 평단가를 계산.


* **매도 (실현 손익):** 단순 매도 금액이 아닌, 평단가 대비 실제 수익금을 계산하여 반환.



## 3. 코드 구조 (Code Structure)

```python
class Portfolio:
    commission_rate = 0.01  # 클래스 변수 (수수료 1%)

    def __init__(self):
        self.__balance = ... # Private 변수 (캡슐화)

    def buy(self):
        # 이동평균법을 이용한 평단가 계산 로직
        pass

    def sell(self):
        # 실현 손익 계산 및 반환
        pass

class VIPPortfolio(Portfolio): # 상속
    commission_rate = 0.0  # 오버라이딩 (수수료 무료)

```

## 4. 트러블 슈팅 (Troubleshooting) & 회고

### 🔥 발생했던 문제 (Issue)

1. **논리 오류 (Logic Error):** 매수 로직 구현 중 `총 비용 = 매수금액 + 수수료율(0.01)`로 잘못 계산하여, 실제 수수료 금액이 차감되지 않는 문제 발생.
2. **문법 오류 (Syntax Error):** 딕셔너리 초기화 시 `self.holdings[ticker] : {...}`와 같이 콜론(`:`)을 잘못 사용하여 `KeyError` 발생.
3. **스코프 오류 (Scope Error):** 클래스 변수 `commission_rate`에 접근할 때 `self`를 붙이지 않아 `NameError` 발생.

### 💡 해결 및 배운 점 (Learned)

* **디버깅:** 수식에서 변수 타입(금액 vs 비율)을 명확히 구분해야 함을 인지하고 `amount * rate`로 수수료 금액을 먼저 계산하도록 수정함.
* **객체지향:** 데이터(변수)를 객체 내부에 숨기는 것이 왜 '보안'에 도움이 되는지, 상속이 어떻게 코드의 양을 획기적으로 줄여주는지 체감함.
* **도메인 지식:** 단순한 코딩 문법보다 주식 거래의 흐름(매수 -> 평단 갱신 -> 잔고 차감)을 논리적으로 설계하는 것이 더 중요하다는 것을 깨달음.

## 5. 향후 발전 계획 (Future Work)

* **데이터 분석 연동:** 거래 내역(History)을 리스트에 저장하고 `Pandas DataFrame`으로 변환하여 수익률 추이 분석.
* **ROI 계산:** 매도 시 단순 이익금뿐만 아니라 `(수익 / 원금) * 100`을 통해 수익률(%) 계산 기능 추가.

---

*Created by [김재천/gorhkdwj]*