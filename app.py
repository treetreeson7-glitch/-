import streamlit as st
import pandas as pd
import json
import os

DATA_FILE = "data.json"
ADMIN_PASSWORD = "1234"

# --- 파일 데이터 불러오기/저장하기 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("correct_answer", 3), data.get("participants", [])
        except Exception:
            return 3, []
    return 3, []

def save_data():
    data = {
        "correct_answer": st.session_state.correct_answer,
        "participants": st.session_state.participants
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

st.set_page_config(
    page_title="선택 비율 공개 실험",
    page_icon="📊",
    layout="centered"
)

# Custom CSS 적용
st.markdown("""
    <style>
    .status-badge {
        background: linear-gradient(135deg, #3182CE 0%, #2B6CB0 100%);
        color: white;
        padding: 6px 18px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 15px;
    }
    .rule-card {
        background: #F7FAFC;
        border-radius: 12px;
        padding: 20px;
        border-left: 6px solid #3182CE;
        margin-bottom: 24px;
    }
    .stButton>button {
        width: 100%;
        height: 3.2em;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
    }
    .stMarkdown, p, span { word-break: keep-all !important; white-space: normal !important; }
    </style>
""", unsafe_allow_html=True)

saved_answer, saved_participants = load_data()

if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = saved_answer

if "participants" not in st.session_state:
    st.session_state.participants = saved_participants

if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "current_stage" not in st.session_state:
    st.session_state.current_stage = 1

if "remaining_options" not in st.session_state:
    st.session_state.remaining_options = [1, 2, 3, 4, 5]

if "current_logs" not in st.session_state:
    st.session_state.current_logs = []

if "test_outcome" not in st.session_state:
    st.session_state.test_outcome = None

if "admin_authenticated" not in st.session_state:
    st.session_state.admin_authenticated = False


def get_stage_denominator(stage):
    count = 0
    for p in st.session_state.participants:
        if len(p["logs"]) >= stage:
            count += 1
    return count

def get_stage_choice_stats(stage):
    denom = get_stage_denominator(stage)
    if denom == 0:
        return None, 0

    counts = {i: 0 for i in range(1, 6)}
    for p in st.session_state.participants:
        if len(p["logs"]) >= stage:
            chosen = p["logs"][stage - 1]["chosen_option"]
            counts[chosen] += 1

    stats = {opt: (cnt / denom) * 100 for opt, cnt in counts.items()}
    return stats, denom

def reset_current_participant():
    st.session_state.current_stage = 1
    st.session_state.remaining_options = [1, 2, 3, 4, 5]
    st.session_state.current_logs = []
    st.session_state.test_outcome = None


# --- 사이드바 메인 메뉴 ---
st.sidebar.markdown("### 📌 메뉴")
menu = st.sidebar.radio("", ["🎮 참가자 실험 참여", "🔒 진행자 관리"])

if menu == "🔒 진행자 관리":
    st.session_state.mode = "admin"
elif menu == "🎮 참가자 실험 참여" and st.session_state.mode == "admin":
    st.session_state.mode = "home"


# 0. 처음 화면
if st.session_state.mode == "home":
    st.title("📊 선택 비율 공개 실험")
    st.caption("확률과 통계 수행평가: 정보 노출에 따른 의사결정 실험")

    st.markdown("""
        <div class="rule-card">
            <h3>🎮 실험 규칙 안내</h3>
            <p>• <b>1번부터 5번</b> 중 단 1개의 숨겨진 <b>정답 선지</b>가 존재합니다.</p>
            <p>• 여러분의 목표는 <b>정답을 끝까지 남기고 오답 선지 4개를 차례대로 제외</b>하는 것입니다.</p>
            <p>• 각 차수마다 <b>이전 참가자들이 선택했던 비율(%) 정보</b>가 제공됩니다.</p>
            <p>• 중간에 <b>정답 선지를 실수로 제외하면 즉시 탈락</b>하게 되니 신중히 선택하세요!</p>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚀 실험 시작하기", type="primary"):
        reset_current_participant()
        st.session_state.mode = "test"
        st.rerun()


# 1. 진행자 관리 화면
elif st.session_state.mode == "admin":
    st.title("🔒 진행자 관리 화면")

    if not st.session_state.admin_authenticated:
        st.info("진행자 전용 메뉴입니다. 인증 비밀번호를 입력해주세요.")

        with st.form(key="admin_login_form"):
            input_pw = st.text_input("비밀번호 입력", type="password")
            submit_button = st.form_submit_button("🔓 인증하기", type="primary")

            if submit_button:
                if input_pw == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.success("인증에 성공했습니다!")
                    st.rerun()
                else:
                    st.error("비밀번호가 올바르지 않습니다.")
    else:
        st.caption("확률과 통계 수행평가 대시보드")
        if st.sidebar.button("🔒 관리자 로그아웃"):
            st.session_state.admin_authenticated = False
            st.rerun()

        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🎯 정답 설정")
            new_ans = st.selectbox(
                "모든 참가자에게 적용될 정답 선지:",
                options=[1, 2, 3, 4, 5],
                index=st.session_state.correct_answer - 1,
                format_func=lambda x: f"{x}번"
            )
            if new_ans != st.session_state.correct_answer:
                st.session_state.correct_answer = new_ans
                save_data()
            st.success(f"현재 설정된 정답: **{st.session_state.correct_answer}번**")

        with col2:
            st.subheader("👥 참가자 현황")
            st.metric(label="누적 완료 참가자", value=f"{len(st.session_state.participants)} 명")

        st.divider()

        tab1, tab2 = st.tabs(["📊 누적 통계 데이터", "📋 참가자별 상세 기록"])

        with tab1:
            total_p = len(st.session_state.participants)

            if total_p > 0:
                outcomes = {"1차 탈락": 0, "2차 탈락": 0, "3차 탈락": 0, "4차 탈락": 0, "최종 성공": 0}
                for p in st.session_state.participants:
                    res = p["result_summary"]
                    if res == "최종 성공":
                        outcomes["최종 성공"] += 1
                    else:
                        outcomes[f"{res[0]}차 탈락"] += 1

                st.write("#### 📌 최종 결과 분포")
                for k, v in outcomes.items():
                    st.write(f"- **{k}**: {v}명 ({(v/total_p)*100:.1f}%)")

                st.divider()
                st.write("#### 📈 차수별 선택 집계")

                for stage in range(1, 5):
                    denom = get_stage_denominator(stage)
                    st.write(f"**[{stage}차]** 도달 참가자 수: **{denom}명**")

                    if denom > 0:
                        counts = {i: 0 for i in range(1, 6)}
                        for p in st.session_state.participants:
                            if len(p["logs"]) >= stage:
                                counts[p["logs"][stage-1]["chosen_option"]] += 1

                        for i in range(1, 6):
                            rate = (counts[i] / denom) * 100
                            st.write(f"- **{i}번**: {counts[i]}회 제외 ({rate:.1f}%)")
                    else:
                        st.info("해당 차수 데이터 없음")

                st.divider()
                st.write("#### 📝 설문 조사 응답 집계")
                survey_counts = {"도움이 되었다": 0, "잘 모르겠다": 0, "도움이 되지 않았다": 0}
                for p in st.session_state.participants:
                    ans = p.get("survey", "")
                    if ans in survey_counts:
                        survey_counts[ans] += 1

                for q_ans, q_cnt in survey_counts.items():
                    st.write(f"- **{q_ans}**: {q_cnt}명 ({(q_cnt/total_p)*100:.1f}%)")

            else:
                st.info("아직 누적된 실험 데이터가 없습니다.")

        with tab2:
            if st.session_state.participants:
                for p in st.session_state.participants:
                    with st.expander(f"👤 참가자 #{p['id']} (결과: {p['result_summary']})"):
                        st.markdown(f"**설문 응답:** `{p.get('survey', '미응답')}`")
                        st.write("**차수별 선택 기록:**")
                        for log in p["logs"]:
                            st.write(f"- **{log['stage']}차**: {log['chosen_option']}번 제외 (노출 비율: **{log['displayed_rate_str']}**)")
            else:
                st.info("기록된 참가자가 없습니다.")

        st.divider()

        with st.expander("⚠️ 데이터 초기화"):
            st.warning("경고: 초기화 시 전체 누적 데이터가 모두 삭제됩니다.")
            confirm = st.checkbox("데이터를 초기화합니다.")
            if st.button("🗑️ 전체 데이터 초기화", disabled=not confirm):
                st.session_state.participants = []
                save_data()
                reset_current_participant()
                st.success("데이터가 초기화되었습니다.")
                st.rerun()


# 2. 참가자 실험 화면
elif st.session_state.mode == "test":
    stage = st.session_state.current_stage
    st.markdown(f"<div class='status-badge'>STAGE {stage} / 4</div>", unsafe_allow_html=True)
    st.title(f"{stage}차 — 제외할 선지 선택")
    st.write("정답이 아니라고 판단되는 선지 **1개**를 선택하여 제외하세요.")

    stats, denom = get_stage_choice_stats(stage)

    if stats is None or denom == 0:
        displayed_rates = {i: "데이터 없음" for i in range(1, 6)}
    else:
        displayed_rates = {i: f"{stats[i]:.1f}%" for i in range(1, 6)}

    st.divider()

    for opt in range(1, 6):
        if opt in st.session_state.remaining_options:
            rate_text = displayed_rates[opt]

            with st.container():
                col_info, col_btn = st.columns([3, 2])
                with col_info:
                    st.markdown(f"### {opt}번 선지")
                    if "데이터 없음" in rate_text:
                        st.caption(f"이전 참가자 선택률: {rate_text}")
                    else:
                        st.markdown(f"이전 참가자 선택률: **{rate_text}**")

                with col_btn:
                    if st.button(f"❌ {opt}번 제외", key=f"btn_{stage}_{opt}"):
                        st.session_state.current_logs.append({
                            "stage": stage,
                            "chosen_option": opt,
                            "displayed_rate_str": displayed_rates[opt]
                        })

                        if opt == st.session_state.correct_answer:
                            st.session_state.test_outcome = f"{stage}차 탈락"
                            st.session_state.mode = "survey"
                            st.rerun()
                        else:
                            st.session_state.remaining_options.remove(opt)
                            if stage == 4:
                                st.session_state.test_outcome = "최종 성공"
                                st.session_state.mode = "survey"
                                st.rerun()
                            else:
                                st.session_state.current_stage += 1
                                st.rerun()
            st.divider()


# 3. 설문 조사 화면
elif st.session_state.mode == "survey":
    st.title("📝 설문 조사")
    st.write("실험이 완료되었습니다! 간단한 설문에 응답해 주세요.")
    st.divider()

    st.subheader("선택 비율 정보가 선지를 제외하는 데 도움이 되었나요?")

    survey_options = ["도움이 되었다", "잘 모르겠다", "도움이 되지 않았다"]
    survey_choice = st.radio(
        "",
        options=survey_options,
        format_func=lambda x: f"① {x}" if x == "도움이 되었다" else (f"② {x}" if x == "잘 모르겠다" else f"③ {x}")
    )

    st.divider()

    if st.button("제출 및 결과 확인", type="primary"):
        participant_id = len(st.session_state.participants) + 1
        new_record = {
            "id": participant_id,
            "result_summary": st.session_state.test_outcome,
            "logs": st.session_state.current_logs,
            "survey": survey_choice
        }
        st.session_state.participants.append(new_record)
        save_data()
        st.session_state.mode = "result"
        st.rerun()


# 4. 최종 결과 화면
elif st.session_state.mode == "result":
    st.title("🎉 실험 결과")
    st.divider()

    outcome = st.session_state.test_outcome
    if outcome == "최종 성공":
        st.balloons()
        st.success("🏆 축하합니다! 정답을 안 지우고 끝까지 성공하셨습니다!")
    else:
        st.error(f"아쉽게도 **{outcome}** 하셨습니다. (정답 선지를 제외함)")

    st.write("### 📋 내가 선택한 기록")
    for log in st.session_state.current_logs:
        st.write(f"- **{log['stage']}차 제외 선지**: {log['chosen_option']}번 (당시 확인한 선택률: **{log['displayed_rate_str']}**)")

    p_last = st.session_state.participants[-1]
    st.write(f"**설문 응답:** `{p_last['survey']}`")

    st.divider()

    if st.button("🔄 처음 화면으로 돌아가기", type="primary"):
        reset_current_participant()
        st.session_state.mode = "home"
        st.rerun()
