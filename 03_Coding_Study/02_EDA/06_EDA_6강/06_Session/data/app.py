# app.py
import json
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="No-show Predictor", layout="centered")
st.title("병원 예약 No-show 예측기")
st.caption("입력값을 넣으면 예측 결과와 No-show 확률을 바로 확인합니다.")

# =========================
# 0) 피처 한글 라벨 매핑 (여기만 수정/추가하면 UI 전체에 반영)
# =========================
FEATURE_KO = {
    # 공통(이번 프로젝트에서 자주 쓰는 형태)
    "age": "나이",
    "gender": "성별",
    "wait_days": "대기일수(예약~진료)",
    "sms_received": "SMS 수신 여부",
    "scholarship": "장학/복지 지원 여부",
    "hypertension": "고혈압 여부",
    "hipertension": "고혈압 여부(원본 철자)",
    "diabetes": "당뇨 여부",
    "alcoholism": "알코올 중독 여부",
    "handcap": "장애 여부(원본 컬럼명)",
    "handicap": "장애 여부",
    # 원본 데이터셋에서 종종 등장(있으면 한글로 같이 표시)
    "neighbourhood": "거주 지역",
    "scheduledday": "예약 등록 일시",
    "appointmentday": "진료(예약) 일시",
    "patient_id": "환자 ID",
    "appointmentid": "예약 ID",
    "no-show": "노쇼(타깃)",
    "noshow": "노쇼(타깃)",
}


def ko_label(col: str) -> str:
    """
    화면에 보여줄 라벨: '컬럼명 (한글해석)'
    - 매핑이 없으면 컬럼명만 표시
    """
    key = col.lower()
    if key in FEATURE_KO:
        return f"{col} ({FEATURE_KO[key]})"
    return col


# =========================
# 1) 모델/메타 로드
# =========================
@st.cache_resource
def load_artifacts():
    model = joblib.load("no_show_pipeline.joblib")
    with open("no_show_meta.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
    return model, meta


model, meta = load_artifacts()
feature_columns = meta["feature_columns"]
schema = meta["schema"]
defaults = meta["defaults"]
label_map = meta.get("label_map", {0: "Show", 1: "No-show"})

# =========================
# 2) UI 설정
# =========================
st.subheader("입력")

threshold = st.slider("판정 임계값 (No-show 확률 기준)", 0.0, 1.0, 0.5, 0.01)

# 0/1 컬럼을 라디오로 보여주고 싶을 때(사용자 편의)
binary_ui = st.checkbox("0/1 값은 Yes/No 라디오로 표시", value=True)

# (선택) 기본으로 노출할 컬럼들: 있으면 우선 보여줌
preferred = [
    "Gender",
    "Age",
    "Scholarship",
    "Hipertension",
    "Hypertension",
    "Diabetes",
    "Alcoholism",
    "Handcap",
    "SMS_received",
    "wait_days",
    "gender",
    "age",
    "scholarship",
    "hipertension",
    "hypertension",
    "diabetes",
    "alcoholism",
    "handcap",
    "sms_received",
]
basic_cols = [c for c in preferred if c in feature_columns]
if not basic_cols:
    basic_cols = feature_columns[:8]  # fallback

# 0/1 라디오 후보 컬럼(원하면 추가/삭제)
binary_name_hints = {
    "sms_received",
    "sms",
    "scholarship",
    "hipertension",
    "hypertension",
    "diabetes",
    "alcoholism",
    "handcap",
    "handicap",
    "is_",
    "has_",
    "_flag",
    "_yn",
    "_yes",
    "_no",
}

# 세션 상태: 입력값 유지
if "user_row" not in st.session_state:
    st.session_state.user_row = defaults.copy()


def is_binary_like(col_name: str, current_val) -> bool:
    """서빙 시점에 X_train이 없으므로, 컬럼명/현재값으로 0/1 여부를 실무적으로 추정."""
    if not binary_ui:
        return False

    name = col_name.lower()

    # 1) 이름 힌트 매칭
    if any(h in name for h in binary_name_hints):
        return True

    # 2) 현재 기본값이 0/1이면 라디오로 보여주기(보수적으로)
    try:
        v = float(current_val)
        if v in (0.0, 1.0):
            return True
    except Exception:
        pass

    return False


def make_widget_key(col: str, suffix: str) -> str:
    """Streamlit 위젯 key 충돌 방지용"""
    return f"{suffix}__{col}"


def render_input_widget(col: str, section: str):
    """
    컬럼 1개 입력 위젯 생성
    - section: 'basic' / 'adv' 등 구분용(위젯 key 충돌 방지)
    - st.session_state.user_row[col] 업데이트
    """
    col_schema = schema[col]
    current = st.session_state.user_row.get(col, defaults.get(col))

    label = ko_label(col)
    key = make_widget_key(col, section)

    # ---- Categorical: 드롭다운/라디오 ----
    if col_schema["type"] == "cat":
        options = col_schema.get("options", [])
        current_str = "" if current is None else str(current)

        if options:
            if current_str not in options:
                options = [current_str] + options

            # 옵션 수가 적으면 radio, 많으면 dropdown
            if len(options) <= 4:
                st.session_state.user_row[col] = st.radio(
                    label, options, index=options.index(current_str), key=key
                )
            else:
                st.session_state.user_row[col] = st.selectbox(
                    label, options, index=options.index(current_str), key=key
                )
        else:
            st.session_state.user_row[col] = st.text_input(
                label, value=current_str, key=key
            )

        return

    # ---- Numeric: number_input 또는 (0/1이면) Yes/No radio ----
    if is_binary_like(col, current):
        try:
            v = int(float(current))
            v = 1 if v == 1 else 0
        except Exception:
            v = 0

        choice = st.radio(
            label, ["No (0)", "Yes (1)"], index=1 if v == 1 else 0, key=key
        )
        st.session_state.user_row[col] = 1 if choice.startswith("Yes") else 0
        return

    # 일반 숫자 입력
    try:
        value = float(current) if current is not None else 0.0
    except Exception:
        value = 0.0

    st.session_state.user_row[col] = st.number_input(label, value=value, key=key)


# =========================
# 3) 입력 폼
# =========================
with st.form("input_form"):
    st.write("기본 입력(자주 쓰는 항목)")

    for col in basic_cols:
        render_input_widget(col, section="basic")

    with st.expander("Advanced (나머지 컬럼도 직접 수정)"):
        remaining = [c for c in feature_columns if c not in basic_cols]
        for col in remaining:
            render_input_widget(col, section="adv")

    col1, col2 = st.columns(2)
    submit = col1.form_submit_button("예측하기")
    reset = col2.form_submit_button("기본값으로 초기화")

if reset:
    st.session_state.user_row = defaults.copy()
    # 위젯 상태도 초기화하고 싶으면 새로고침이 가장 깔끔
    st.rerun()

# =========================
# 4) 예측 & 결과 출력
# =========================
if submit:
    # 모델이 기대하는 컬럼 순서대로 1행 DataFrame 구성
    row = []
    for c in feature_columns:
        val = st.session_state.user_row.get(c, defaults.get(c))

        if schema[c]["type"] == "num":
            try:
                val = float(val)
            except Exception:
                val = 0.0
        else:
            val = "" if val is None else str(val)

        row.append(val)

    X_one = pd.DataFrame([row], columns=feature_columns)

    proba_no_show = None
    if hasattr(model, "predict_proba"):
        proba_no_show = float(model.predict_proba(X_one)[0][1])  # class=1 확률
        pred = int(proba_no_show >= threshold)
    else:
        pred = int(model.predict(X_one)[0])

    st.divider()
    st.subheader("예측 결과")

    st.write(f"예측 라벨: **{label_map.get(pred, pred)}** (raw={pred})")

    if proba_no_show is not None:
        st.metric("No-show 확률", f"{proba_no_show:.4f}")
        st.write(
            f"임계값 **{threshold:.2f}** 기준 판정: **{label_map.get(pred, pred)}**"
        )

    with st.expander("입력값(모델에 전달된 1행) 보기"):
        # 보기 편하게 컬럼명을 '영문 (한글)'로 바꿔서 표로 표시(모델 입력은 원본 X_one 사용)
        X_show = X_one.copy()
        X_show.columns = [ko_label(c) for c in X_show.columns]
        st.dataframe(X_show)
