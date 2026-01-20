# 📂 PJ05_Fintech_Data_Pipeline

**(부제: 지저분한 주식 거래 로그 정제 및 가중평균(VWAP) 산출 시스템)**

> **"쓰레기 데이터(Garbage In)를 황금 같은 정보(Gold Out)로."**
> 기존의 수작업 전처리가 가진 비효율성과 휴먼 에러를 해결하기 위해, **Pandas & OOP** 기반으로 구축한 자동화된 금융 데이터 정제 파이프라인입니다.

---

## 1. Project Overview

* **프로젝트 명:** PJ05_Fintech_Data_Pipeline
* **수행 기간:** 2026.01.21 (1일)

### 💼 가상 시나리오 (Scenario)
> **"고객님 계좌 잔고가 왜 이러죠? 시스템 오류인가요?"**
>
> 당신은 핀테크 스타트업 **'QuantLab'**의 주니어 데이터 엔지니어입니다.
> 오늘 아침, 제휴 증권사로부터 어제 자 **고객 주식 거래 내역(Raw Data)** 파일이 도착했지만, 레거시 시스템의 오류로 인해 날짜 포맷이 섞이고 가격 데이터가 유실되는 등 **데이터가 엉망진창(Dirty)**인 상태입니다.
>
> 팀장님은 **"2시간 내에 데이터를 완벽하게 전처리하고, 종목별 정확한 평단가(VWAP)를 계산해 달라"**는 긴급 요청을 보냈습니다. 당신의 임무는 이 'Dirty Data'를 분석 가능한 정보로 바꾸는 견고한 **데이터 파이프라인**을 구축하는 것입니다.

* **목표:**
  1. 이질적인 날짜/문자열 포맷을 통일하는 **데이터 정규화 (Standardization)**
  2. 단순 0이 아닌 '종목별 평균가'를 활용한 논리적 **결측치 보간 (Imputation)**
  3. 거래량을 반영하여 시장의 실제 체결 단가를 파악하는 **VWAP 산출 (Financial Metrics)**

---

## 2. Tech Stack & Concepts
본 프로젝트에 사용된 주요 기술과 핵심 개념입니다.

* **Language & Library:** Python 3.12, Pandas, NumPy
* **OOP (Object-Oriented Programming):**
    * `DataCleaner` 클래스를 설계하여 전처리 로직을 캡슐화하고 재사용성을 확보했습니다.
* **Advanced Pandas Techniques:**
    * `map`: 대량의 데이터를 고속으로 매핑(Dictionary Mapping) 처리.
    * `transform`: 그룹별 집계 연산 후 원본 차원을 유지하여 결측치 보간에 활용.
    * `format='mixed'`: 다양한 날짜 형식이 혼재된 데이터를 유연하게 파싱.

---

## 3. Implementation Details
데이터 파이프라인은 크게 **주입(Injection) -> 정제(Cleaning) -> 분석(Analysis)** 단계로 구성됩니다.

### Step 1: Raw Data Injection
입력 데이터(`df_raw`)는 날짜 형식이 제각각(`-`, `/`, `.`)이고, 매수/매도 표기가 통일되지 않았으며(`Buy`, `B`, `sell`), 가격에 특수문자나 결측치(NaN)가 포함된 상태입니다.

### Step 2: Preprocessing (DataCleaner Class)
객체지향 설계를 통해 다음과 같은 메서드로 데이터를 정제합니다.

1.  **`clean_date`**: `pd.to_datetime(..., format='mixed')`을 사용하여 `NaT` 데이터를 처리하고 유효한 날짜만 남깁니다.
2.  **`clean_side`**: `buy/sell`, `B/S` 등으로 혼재된 데이터를 `.map()`을 통해 `True(매수)/False(매도)` 불리언 값으로 표준화합니다.
3.  **`clean_price`**: 문자열 내 쉼표(`,`)를 제거하고 수치형(`float`)으로 변환합니다. `errors='coerce'`로 오류를 방어합니다.
4.  **`fill_missing_price`**: **`groupby('ticker')['price'].transform('mean')`**을 사용하여, 결측치를 해당 종목의 평균 가격으로 논리적으로 채웁니다.

### Step 3: VWAP Analysis
정제된 데이터를 바탕으로 가중평균가격을 계산합니다.
* **공식:** $VWAP = \frac{\sum(\text{Price} \times \text{Qty})}{\sum \text{Qty}}$
* 단순 평균이 아닌, 거래량이 많이 실린 가격대에 가중치를 두어 실제 시장가(Market Consensus)를 도출합니다.

---

## 4. Troubleshooting
프로젝트 진행 중 발생한 주요 이슈와 해결 과정입니다.

### Issue 1: CSV 저장/로드 시 'Leading Zero' 소실
* **Problem:** 종목코드 `'005930'`(삼성전자)이 CSV 저장 후 다시 로드할 때 정수 `5930`으로 변환되어 앞자리 `0`이 사라지는 현상 발생.
* **Cause:** CSV는 타입 정보를 저장하지 않으며, Pandas는 로드 시 숫자로 구성된 문자열을 `int`로 자동 형변환(Type Inference)함.
* **Fix:** `read_csv` 시 **`dtype={'ticker': str}`** 옵션을 명시하여 강제로 문자열로 인식하도록 수정. (향후 Parquet 포맷 도입 고려)

### Issue 2: OOP 클래스 스코프(Scope) 오류
* **Problem:** `DataCleaner` 클래스 메서드 내부에서 인스턴스 변수 접근 시 `NameError` 발생.
* **Cause:** `self` 키워드를 누락하여 지역 변수나 전역 변수를 참조하려 했음.
* **Fix:** 클래스 내부의 모든 데이터프레임 접근 코드를 **`self.df`**로 통일하여 캡슐화 원칙 준수.

---

## 5. Retrospective & Insights
### Domain Knowledge: "평균의 함정" 탈출
주식 시장에서 단순 평균(Simple Mean)은 거래량을 무시하여 시장 상황을 왜곡할 수 있습니다. 이번 프로젝트를 통해 **"돈(거래량)이 많이 실린 가격이 진짜 가격이다"**라는 VWAP의 핵심 의미를 이해했습니다.

### Tech Insight: "Robust(견고한) 파이프라인"
`errors='coerce'`와 `format='mixed'` 옵션을 적극 활용하여, 예측 불가능한 더러운 데이터(Dirty Data)가 유입되더라도 파이프라인이 중단되지 않고 유연하게 대처하도록 설계하는 방법을 익혔습니다.

### Data Integrity
결측치를 단순히 `0`으로 채우는 것은 분석 결과를 망치는 지름길입니다. 도메인 맥락(같은 종목의 평균가)을 고려한 **논리적인 Imputation 전략**이 데이터의 품질을 결정함을 배웠습니다.

---

## 6. Future Work
본 프로젝트의 기능을 확장하여 실제 트레이딩 시스템에 가까운 형태로 고도화할 계획입니다.

* **데이터 분석 연동 (History Analytics):**
    * 누적된 거래 내역(History)을 리스트에 저장하고 `Pandas DataFrame`으로 변환.
    * Matplotlib/Seaborn을 연동하여 기간별 **수익률 추이 시각화** 기능 구현.
* **ROI 지표 고도화 (Advanced Metrics):**
    * 현재의 평단가 계산을 넘어, 매도 시점의 단순 이익금뿐만 아니라 정확한 수익률을 계산.
    * 공식 적용: $\frac{\text{수익(Profit)}}{\text{투자 원금(Principal)}} \times 100 (\%)$

---

## 7. Project Structure
```bash
├── PJ05_Fintech_Data_Pipeline.ipynb  # 메인 코드 및 분석 리포트
├── data/
│   ├── PJ05_Cleaned_Fintech_Data.csv # 전처리 완료 데이터
│   └── PJ05_VWAP_Fintech_Data.csv    # 최종 결과 (VWAP 리포트)
└── README.md                         # 프로젝트 문서
```
*Created by [김재천/gorhkdwj]*