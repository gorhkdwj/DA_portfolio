# PJ03. Smart Portfolio Refactoring (함수와 모듈화)

## 1. 프로젝트 개요
- **프로젝트 명:** 주식 거래 시뮬레이터 리팩토링 (Spaghetti to Clean Code)
- **목표:** 전역 변수로 뒤범벅된 '스파게티 코드'를 유지보수 가능한 '함수형 코드'로 재설계한다.
- **핵심 기술:** Python (`def`, `return`, Scope), Data Structure (`Dictionary`), Logic (이동평균법)

## 2. 프로젝트 스토리 (Scenario)
> "전임자가 남기고 간 주식 거래 코드는 함수 밖의 변수(Global Variable)를 마구잡이로 수정해서, 실행할 때마다 데이터가 꼬이는 문제가 있었습니다. 이를 해결하기 위해 **Input(매개변수)과 Output(반환값)**이 명확한 순수 함수 형태로 리버스 엔지니어링을 수행했습니다."

## 3. 핵심 구현 내용

### 3.1. 메모리 참조 문제 해결 (Initialization)
- **문제:** `dict.fromkeys()`로 포트폴리오를 초기화하면, 모든 종목이 동일한 내부 딕셔너리 주소를 공유하여 데이터가 같이 수정되는 치명적 버그 발생.
- **해결:** **Dictionary Comprehension**을 사용하여 각 종목마다 '새로운' 딕셔너리를 생성하도록 수정.

```python
# [Bad] 모든 키가 같은 객체를 바라봄
# portfolio = dict.fromkeys(tickers, {'qty': 0, ...}) 

# [Good] 반복될 때마다 새로운 객체 생성
portfolio = {ticker: {'qty': 0, 'avg_price': 0.0} for ticker in tickers}
```
3.2. 평단가 계산 로직 (Moving Average)
매수 시마다 달라지는 평단가를 계산하기 위해 이동평균법(Weighted Average) 공식을 적용. 
$$ \text{New Avg} = \frac{(\text{Old Qty} \times \text{Old Avg}) + (\text{Buy Qty} \times \text{Buy Price})}{\text{Old Qty} + \text{Buy Qty}} $$

3.3. 데이터 흐름 제어 (Return)
함수 내부에서 외부 변수를 직접 수정하지 않고, **갱신된 데이터를 return**하여 호출한 쪽에서 받아가도록 구조 변경.

```Python

# 매수 후 갱신된 지갑과 잔고를 반환
return portfolio, balance
```
4. 트러블 슈팅 (Troubleshooting)
4.1. Return의 위치 (Indentation Error)
문제: return 문을 else 블록 안에 넣었더니, 잔고 부족 등 예외 상황(if) 발생 시 함수가 None을 반환하며 프로그램이 종료됨.

해결: 성공/실패 여부와 관계없이 항상 현재 상태를 반환하도록 return의 들여쓰기 레벨을 함수 최상위로 조정함.

4.2. 중첩 딕셔너리 접근 (Nested Dict)
문제: portfolio[ticker]까지는 접근했으나, 그 안의 수량을 꺼낼 때 문법 혼동.

해결: 대괄호를 두 번 사용하여(portfolio[ticker]['qty']) 정확한 주소값에 접근.

5. 결과 (Output)
모듈화된 함수 덕분에 삼성전자, 하이닉스 등 여러 종목을 섞어서 거래해도 데이터 간섭 없이 정확한 수익률 계산 가능.

initialize -> buy -> sell로 이어지는 데이터 파이프라인 구축 완료.