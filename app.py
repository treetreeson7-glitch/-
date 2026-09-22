import streamlit as st
import pandas as pd
import json
import os
import re

DATA_FILE = "data.json"
ADMIN_PASSWORD = "1234"  # 진행자 비밀번호

# 허용되는 앞 3자리 및 뒤 2자리 정의
VALID_CLASS_PREFIXES = {f"2{i:02d}" for i in range(1, 13)}  # '201' ~ '212'
VALID_NUMBER_SUFFIXES = {f"{i:02d}" for i in range(1, 33)}   # '01' ~ '32'

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

# Page Config
st.set_page_config(
    page_title="가짜 번호 제외하기 게임",
    page_icon="📊",
    layout="centered"
)

# Custom CSS - 라이트/다크 모드 및 st.form_submit_button 완벽 스타일링
st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* 1. 전체 앱 기본 배경 및 폰트 고정 */
    html, body, [data-testid="stAppViewContainer"], .main, .stApp {
        background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 100%) !important;
        color: #F8FAFC !important;
        font-family: 'Pretendard', sans-serif !important;
    }

    /* 2. 상단 헤더 및 툴바 투명화 */
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: transparent !important;
        color: #F8FAFC !important;
    }

    /* 3. 사이드바 배경 및 내부 텍스트 완벽 고정 */
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }
    [data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    /* 4. 모든 텍스트/헤더 요소 흰색 선명하게 고정 */
    h1, h2, h3, h4, h5, h6, p, span, div, label, .stMarkdown, .stCaption {
        color: #F8FAFC !important;
        word-break: keep-all !important;
        white-space: normal !important;
    }
    
    .stCaption, caption {
        color: #94A3B8 !important;
    }

    /* 5. 카드 및 뱃지 디자인 */
    .status-badge {
        background: linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%);
        color: #FFFFFF !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 800;
        font-size: 0.85rem;
        letter-spacing: 1px;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    .rule-card {
        background: rgba(30, 41, 59, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 24px;
        border-left: 6px solid #8B5CF6 !important;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .rule-card h3, .rule-card p, .rule-card b {
        color: #F8FAFC !important;
    }
    
    .highlight-card {
        background: rgba(99, 102, 241, 0.15) !important;
        border: 1px solid rgba(139, 92, 246, 0.4) !important;
        border-radius: 12px;
        padding: 16px 20px;
        margin-top: 12px;
        margin-bottom: 16px;
    }

    /* 6. 입력창(Text Input) 라벨 및 본문 강제 고정 */
    [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }
    .stTextInput input {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
        border: 1px solid #64748B !important;
        border-radius: 10px !important;
    }
    .stTextInput input::placeholder {
        color: #94A3B8 !important;
    }

    /* 7. 라디오/선택 버튼 글자색 고정 */
    [data-testid="stRadioButton"] label p {
        color: #F8FAFC !important;
    }

    /* 8. 일반 버튼 및 Form 제출 버튼(로켓 버튼) 스타일 적용 */
    .stButton>button, [data-testid="stFormSubmitButton"]>button {
        width: 100% !important;
        height: 3.4em !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4) !important;
    }
    .stButton>button:hover, [data-testid="stFormSubmitButton"]>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6) !important;
    }
    .stButton>button *, [data-testid="stFormSubmitButton"]>button * {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

# Session State Initialization
saved_answer, saved_participants = load_data()

if "correct_answer" not in st.session_state:
    st.session_state.correct_answer = saved_answer

if "participants" not in st.session_state:
    st.session_state.participants = saved_participants

if "mode" not in st.session_state:
    st.session_state.mode = "home"

if "current_student_id" not in st.session_state:
    st.session_state.current_student_id = ""

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


def validate_student_id(sid):
    if len(sid) != 5 or not sid.isdigit():
        return False
    prefix = sid[:3]
    suffix = sid[3:]
    return (prefix in VALID_CLASS_PREFIXES) and (suffix in VALID_NUMBER_SUFFIXES)

def is_already_participated(sid):
    for p in st.session_state.participants:
        if p.get("student_id") == sid:
            return True
    return False

def calculate_conditional_stage_stats(stage, current_remaining_options):
    raw_probs = {}
    
    for opt in current_remaining_options:
        appeared_count = 0
        chosen_count = 0
        
        for p in st.session_state.participants:
            if len(p["logs"]) >= stage:
                past_chosen = [log["chosen_option"] for log in p["logs"][:stage - 1]]
                stage_options = [x for x in [1, 2, 3, 4, 5] if x not in past_chosen]
                
                if opt in stage_options:
                    appeared_count += 1
                    if p["logs"][stage - 1]["chosen_option"] == opt:
                        chosen_count += 1
        
        if appeared_count > 0:
            raw_probs[opt] = chosen_count / appeared_count
        else:
            raw_probs[opt] = None

    valid_probs = {k: v for k, v in raw_probs.items() if v is not None}
    if not valid_probs:
        return {opt: "데이터 없음" for opt in current_remaining_options}

    total_sum = sum(valid_probs.values())
    
    if total_sum == 0:
        equal_rate = 100.0 / len(valid_probs)
        return {opt: f"{equal_rate:.1f}%" if opt in valid_probs else "데이터 없음" for opt in current_remaining_options}

    result_rates = {}
    for opt in current_remaining_options:
        if opt in valid_probs:
            normalized_prob = (valid_probs[opt] / total_sum) * 100
            result_rates[opt] = f"{normalized_prob:.1f}%"
        else:
            result_rates[opt] = "데이터 없음"

    return result_rates

def reset_current_participant():
    st.session_state.current_student_id = ""
    st.session_state.current_stage = 1
    st.session_state.remaining_options = [1, 2, 3, 4, 5]
    st.session_state.current_logs = []
    st.session_state.test_outcome = None


# --- 사이드바 메인 메뉴 ---
st.sidebar.markdown("### 📌 Navigation")
menu = st.sidebar.radio("", ["🎮 참가자 실험 참여", "🔒 진행자 관리"])

if menu == "🔒 진행자 관리":
    st.session_state.mode = "admin"
elif menu == "🎮 참가자 실험 참여" and st.session_state.mode == "admin":
    st.session_state.mode = "home"


# ==========================================
# 0. 처음 화면 (규칙 설명 및 학번 입력)
# ==========================================
if st.session_state.mode == "home":
    st.title("📊 여러분의 감을 믿으십니까? 가짜 번호 제외하기 게임")
    st.caption("확률과 통계 수행평가: 정보 제공은 확률의 변화로 이어질까?")

    st.markdown("""
        <div class="rule-card">
            <h3>🎮 실험 규칙 안내</h3>
            <p>• <b>1번부터 5번</b> 중 단 1개의 숨겨진 <b>정답 선지</b>가 존재합니다.</p>
            <p>• 여러분의 목표는 <b>정답을 끝까지 남기고 오답 선지 4개를 차례대로 제외</b>하는 것입니다.</p>
            <p>• 각 차수마다 <b>이전 참가자들이 선택했던 비율(%) 정보</b>가 제공됩니다.</p>
            <p>• 중간에 <b>정답 선지를 실수로 제외하면 즉시 탈락</b>하게 되니 신중히 선택하세요!</p>
        </div>
    """, unsafe_allow_html=True)

    with st.form("student_id_form"):
        st.subheader("👤 학번 입력")
        sid_input = st.text_input(
            "학번 5자리를 입력하세요 (예: 20725, 20718)",
            placeholder="예: 20725",
            max_chars=5
        )
        submit_sid = st.form_submit_button("🚀 실험 시작하기")

        if submit_sid:
            sid_clean = sid_input.strip()
            if not validate_student_id(sid_clean):
                st.error("⚠️ 올바른 학번 형식이 아닙니다. (예: 20725 — 2학년 1~12반, 1~32번 가능)")
            elif is_already_participated(sid_clean):
                st.session_state.current_student_id = sid_clean
                st.session_state.mode = "already_participated"
                st.rerun()
            else:
                reset_current_participant()
                st.session_state.current_student_id = sid_clean
                st.session_state.mode = "test"
                st.rerun()


# ==========================================
# 중복 참여 제재 화면
# ==========================================
elif st.session_state.mode == "already_participated":
    st.title("⚠️ 참여 제한 안내")
    st.divider()
    st.error("❌ 참여는 1회로 제한됩니다.")
    st.info(f"입력하신 학번(**{st.session_state.current_student_id}**)은 이미 실험에 참여하였습니다.")
    st.write("")
    
    if st.button("🔄 처음 화면으로 돌아가기", type="primary"):
        reset_current_participant()
        st.session_state.mode = "home"
        st.rerun()


# ==========================================
# 1. 진행자 관리 화면
# ==========================================
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
                
                # --- [추가] 5명 단위 누적 참가자 수별 최종 성공률 기록 ---
                st.write("#### 🎯 누적 참가자 수별 최종 성공률 (5명 단위 추이)")
                if total_p >= 5:
                    milestone_html = "<div class='highlight-card'><b>📈 참가자 누적 수별 성공률 기록:</b><br/>"
                    for count in range(5, total_p + 1, 5):
                        sub_participants = st.session_state.participants[:count]
                        success_count = sum(1 for p in sub_participants if p["result_summary"] == "최종 성공")
                        success_rate = (success_count / count) * 100
                        milestone_html += f"• <b>{count}명 달성 시점</b>: 누적 성공자 {success_count}명 → <b>{success_rate:.1f}%</b><br/>"
                    milestone_html += "</div>"
                    st.markdown(milestone_html, unsafe_allow_html=True)
                else:
                    st.info("참가자가 5명 이상 집계되면 5명 단위 누적 성공률 추이가 표시됩니다.")

                st.divider()
                st.write("#### 📈 차수별 선택 선지의 평균 선택 비율")

                for stage in range(1, 5):
                    valid_rates = []
                    for p in st.session_state.participants:
                        if len(p["logs"]) >= stage:
                            rate_str = p["logs"][stage - 1]["displayed_rate_str"]
                            match = re.search(r"([0-9]+(?:\.[0-9]+)?)%", rate_str)
                            if match:
                                valid_rates.append(float(match.group(1)))
                    
                    if valid_rates:
                        avg_rate = sum(valid_rates) / len(valid_rates)
                        st.write(f"- **{stage}차**: **{avg_rate:.1f}%**인 선지 선택 (참가자 {len(valid_rates)}명 대상)")
                    else:
                        st.write(f"- **{stage}차**: 수집된 데이터 없음 (초기 참가자 또는 미도달)")

                st.divider()
                st.write("#### 📝 설문 조사 응답 집계 (항목별 상세 결과)")
                
                survey_items = ["도움이 되었다", "잘 모르겠다", "도움이 되지 않았다"]
                
                for item in survey_items:
                    # 해당 항목 응답자 추출
                    item_participants = [p for p in st.session_state.participants if p.get("survey") == item]
                    item_count = len(item_participants)
                    item_pct = (item_count / total_p) * 100 if total_p > 0 else 0
                    
                    st.markdown(f"##### 🔹 **{item}**: {item_count}명 ({item_pct:.1f}%)")
                    
                    if item_count > 0:
                        # 해당 응답 집단 내부 결과 분포
                        item_outcomes = {"1차 탈락": 0, "2차 탈락": 0, "3차 탈락": 0, "4차 탈락": 0, "최종 성공": 0}
                        for p in item_participants:
                            res = p["result_summary"]
                            if res == "최종 성공":
                                item_outcomes["최종 성공"] += 1
                            else:
                                item_outcomes[f"{res[0]}차 탈락"] += 1
                        
                        out_str_list = []
                        for stage_key in ["1차 탈락", "2차 탈락", "3차 탈락", "4차 탈락", "최종 성공"]:
                            cnt = item_outcomes[stage_key]
                            pct = (cnt / item_count) * 100
                            out_str_list.append(f"{stage_key}: {cnt}명({pct:.1f}%)")
                        
                        st.caption("└ " + " | ".join(out_str_list))
                    else:
                        st.caption("└ 응답한 참가자가 없습니다.")

            else:
                st.info("아직 누적된 실험 데이터가 없습니다.")

        with tab2:
            if st.session_state.participants:
                for p in st.session_state.participants:
                    sid_disp = p.get('student_id', '미기재')
                    with st.expander(f"👤 학번 #{sid_disp} (결과: {p['result_summary']})"):
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


# ==========================================
# 2. 참가자 실험 화면
# ==========================================
elif st.session_state.mode == "test":
    stage = st.session_state.current_stage
    st.markdown(f"<div class='status-badge'>STAGE {stage} / 4</div>", unsafe_allow_html=True)
    st.title(f"{stage}차 — 제외할 선지 선택")
    st.caption(f"참가자 학번: {st.session_state.current_student_id}")
    st.write("정답이 아니라고 판단되는 선지 **1개**를 선택하여 제외하세요.")

    displayed_rates = calculate_conditional_stage_stats(stage, st.session_state.remaining_options)

    st.divider()

    for opt in range(1, 6):
        if opt in st.session_state.remaining_options:
            rate_text = displayed_rates.get(opt, "데이터 없음")
            
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
                            "displayed_rate_str": rate_text
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


# ==========================================
# 3. 설문 조사 화면
# ==========================================
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
            "student_id": st.session_state.current_student_id,
            "result_summary": st.session_state.test_outcome,
            "logs": st.session_state.current_logs,
            "survey": survey_choice
        }
        st.session_state.participants.append(new_record)
        save_data()
        st.session_state.mode = "result"
        st.rerun()


# ==========================================
# 4. 최종 결과 화면
# ==========================================
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
    st.write(f"**학번:** `{p_last.get('student_id', '미기재')}`")
    st.write(f"**설문 응답:** `{p_last['survey']}`")

    st.divider()

    if st.button("🔄 처음 화면으로 돌아가기", type="primary"):
        reset_current_participant()
        st.session_state.mode = "home"
        st.rerun()
