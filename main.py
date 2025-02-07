import streamlit as st
from datetime import datetime, timedelta
import pytz

# ✅ 가장 첫 줄에서 페이지 설정 적용
st.set_page_config(page_title="멘토즈 가맹관리부 시스템", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# 한국 시간(KST)으로 변환
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)

# 시간 형식으로 출력
st.write(f'{now.strftime('%Y-%m-%d %H:%M')} [user]')

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True  # 이미 인증되었으면 바로 통과
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    st.markdown("## 🔐 접근 제한")
    password = st.text_input("비밀번호를 입력하세요", type="password", key="login_password", on_change=lambda: st.session_state.update({'login_pressed': True}))
    if st.session_state.get('login_pressed', False) or st.button("로그인"):
        if password == "1234":  # ✅ 여기에 원하는 비밀번호 설정
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다!")
    
    return st.session_state.authenticated

def main():
    if not check_password():
        st.stop() # 인증되지 않으면 이후 코드 실행 안됨
        return  # 인증되지 않으면 실행 안 됨
    
    st.sidebar.markdown(
        """
        <style>
        .sidebar-title {
            font-size: 32px;
            font-weight: bold;
            text-align: center;
            color: #ffffff;
            margin-bottom: 20px;
            padding: 15px;
            background-color: #34495e;
            border-radius: 10px;
        }
        .sidebar-button {
            display: block;
            width: 100%;
            padding: 10px;
            margin: 5px 0;
            font-size: 18px;
            text-align: center;
            border: none;
            border-radius: 5px;
            background-color: #3498db;
            color: white;
            cursor: pointer;
            transition: 0.3s;
        }
        .sidebar-button:hover {
            background-color: #2980b9;
        }
        .stSidebar { background-color: #2c3e50 !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.sidebar.markdown('<p class="sidebar-title">📌 MENU </p>', unsafe_allow_html=True)
    
    if st.sidebar.button("🏠 홈", key="home"):
        st.session_state.page = "home"
    if st.sidebar.button("🔑 사물함 마스터키", key="locker"):
        st.session_state.page = "locker"
    if st.sidebar.button("🔄 퇴실 미처리 복구", key="restore"):
        st.session_state.page = "restore"
    if st.sidebar.button("💰 이용권 환불 계산", key="refund"):
        st.session_state.page = "refund"
    
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "locker":
        locker_masterkey_page()
    elif st.session_state.page == "restore":
        restore_checkout_page()
    elif st.session_state.page == "refund":
        refund_calculator_page()


def home_page():
    st.markdown(
        """
        <style>
        .stApp { background-color: #f5f7fa; }
        .title-text { text-align: center; font-size: 40px; font-weight: bold; color: white; background-color: #2c3e50; padding: 15px; border-radius: 10px; }
        .sub-title { text-align: center; font-size: 20px; color: #ffffff; background-color: #34495e; padding: 10px; border-radius: 10px; }
        .section-header { font-size: 24px; font-weight: bold; color: #2980b9; text-align: center; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<p class="title-text"> 멘토즈 가맹관리부 by.min </p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">📌 편리한 업무를 위한 기능 제공 </p>', unsafe_allow_html=True)
    
    st.markdown("---")

def locker_masterkey_page():
    st.subheader("🔑 사물함 마스터키 안내")
    locker_number = st.text_input("사물함 번호를 입력하세요", key="locker_number", on_change=lambda: st.session_state.update({'locker_submit': True}))
    locker_password = st.text_input("사물함 비밀번호 입력", type="password", key="locker_password", on_change=lambda: st.session_state.update({'locker_submit': True}))
    
    if (st.session_state.get('locker_submit', False) and locker_number and locker_password) or st.button("마스터키 안내 보기"):
        if not locker_number or not locker_password:
            st.error("❌ 사물함 번호와 비밀번호를 입력하세요!")
        else:
            info_text = (
                f"✅ 구매 확인 완료되어,\n"
                f"사물함 마스터키 안내드립니다💛\n\n"
                f"🔑 [{locker_number}]번 사물함에 가셔서\n"
                f"비밀번호 [{locker_password}]을(를) 눌러주시면,\n"
                f"내부에 마스터키가 들어 있습니다.\n"
                "키는 사용 후 제자리에 넣고 다시 [" + locker_password + "] 입력하여 잠금 부탁드립니다.\n\n"
                "✅ 마스터키 사용 방법\n"
                "마스터키를 잠겨있는 사물함의\n"
                "키패드 중간에 보이는 ‘동그란 홈 부분’에 대시면 문이 열립니다.\n\n"
                "✅ 사물함 비밀번호 설정 방법\n"
                "문을 닫고 원하는 비밀번호 4자리를 누르세요.\n"
                "‘설정했던 비밀번호 4자리’를 다시 누르면 문이 열립니다."
            )
            st.text_area("📌 마스터키 안내", info_text, height=250)

import pytz
from datetime import datetime

import streamlit as st
from datetime import datetime
import pytz

def restore_checkout_page():
    st.title("🛠️ 퇴실 미처리 복구")
    checkout_date = st.text_input("퇴실 일자 (YYYYMMDD)")
    checkout_time = st.text_input("퇴실 시간 (HHMM)")

    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)  # 현재 시간을 한국 시간대로 가져오기

    with st.form(key="checkout_form"):
        submit_button = st.form_submit_button("미처리 시간 계산")

    if submit_button:
        try:
            # 사용자가 입력한 퇴실 날짜와 시간 문자열을 datetime 객체로 변환
            checkout_datetime = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y%m%d %H%M")
            checkout_datetime = kst.localize(checkout_datetime)  # 입력된 날짜와 시간을 한국 시간대에 맞게 변환

            if checkout_datetime > now:
                st.error("❌ 퇴실 시간이 미래일 수 없습니다!")
                return

            # 시간 차 계산
            lost_time = now - checkout_datetime
            lost_minutes = int(lost_time.total_seconds() // 60)
            lost_hours = lost_minutes // 60
            remaining_minutes = lost_minutes % 60
            extra_fee = (lost_minutes // 30) * 1000  # 30분당 1000원 초과 요금 계산

            # 결과 출력
            st.success(f"📅 미처리 기간: {checkout_datetime.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}")
            st.success(f"⏳ 미처리 시간: {lost_hours}시간 {remaining_minutes}분")
            st.success(f"💰 초과 요금: {extra_fee:,}원 (30분당 1,000원)")
        except ValueError:
            st.error("❌ 올바른 날짜 및 시간 형식을 입력하세요!")


def refund_calculator_page():
    st.title("💰 이용권 환불 계산")
    
    # 기본 정보 입력
    branch = st.text_input("지점명")
    phone = st.text_input("전화번호")
    ticket_type = st.radio("이용권 종류", ["기간권", "시간권", "노블레스석"])
    policy = st.radio("환불 규정", ["일반", "% 규정"])
    
    # 결제 및 환불 정보 입력 (날짜는 기본값으로 오늘 날짜 설정)
    ticket_price = st.number_input("결제 금액 (원)", min_value=0)
    purchase_date = st.date_input("결제일", value=datetime.now(pytz.timezone('Asia/Seoul')).date())
    refund_date = st.date_input("환불 요청일", value=datetime.now(pytz.timezone('Asia/Seoul')).date())
    
    # 위약금 선택 (0%, 10%, 20%)
    penalty_rate = st.selectbox("위약금 선택", ["0%", "10%", "20%"], index=0)
    
    # 이용권 종류에 따른 추가 입력 필드
    if ticket_type in ["기간권", "노블레스석"]:
        days_given = st.number_input("전체 부여 기간 [일] (기간권/노블레스석)", min_value=1)
    else:
        days_given = None
    
    if ticket_type == "시간권":
        weeks_given = st.number_input("유효 기간 [주] (시간권)", min_value=1)
        hours_used = st.number_input("사용 시간 (시간권)", min_value=0)
        total_hours = st.number_input("전체 부여 시간 (시간권)", min_value=1)
    else:
        weeks_given = None
        hours_used = None
        total_hours = None
    
    if ticket_type == "노블레스석":
        noble_rate = st.number_input("노블레스석 1일 요금 (원)", min_value=0)
    else:
        noble_rate = None
    
    # 유효 기간 계산
    if ticket_type == "시간권":
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(weeks=weeks_given)).strftime('%Y-%m-%d')}"
    else:
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(days=days_given-1)).strftime('%Y-%m-%d')}" if days_given else "정보 없음"
    
    # 이용권 종류 표시 형식 수정
    formatted_ticket_type = f"{ticket_type} ({days_given}일)" if ticket_type != "시간권" else f"{ticket_type} ({total_hours}시간)"
    
    # 환불 금액 계산 (엔터 키로도 실행 가능)
    if st.button("환불 금액 계산"):  # 항상 계산 실행
        used_days = (refund_date - purchase_date).days + 1
        daily_rate = 11000
        hourly_rate = 2000
        used_amount = 0
        
        # 결제일자 30일 초과 시 팝업 알림
        if (refund_date - purchase_date).days > 30:
            st.warning("결제한지 30일이 지났으므로 위약금이 발생하거나, 환불이 불가할 수 있습니다.")
        
        # 환불 규정에 따른 계산
        if policy == "% 규정":
            percent_used = (used_days / days_given) * 100 if ticket_type in ["기간권", "노블레스석"] else (hours_used / total_hours) * 100
            
            if percent_used < 25:
                refund_amount = ticket_price * 0.5
                deduction_amount = ticket_price * 0.5
                deduction_detail = f"0~24% 환불 구간 : 결제금액의 50% 환불 ({deduction_amount:,.0f}원)"
            elif percent_used < 50:
                refund_amount = ticket_price * 0.25
                deduction_amount = ticket_price * 0.75
                deduction_detail = f"25~50% 환불 구간 : 결제금액의 25% 환불 ({deduction_amount:,.0f}원)"
            else:
                refund_amount = 0
                deduction_amount = ticket_price
                deduction_detail = f"50% 이상 사용 구간 : 환불 불가 ({deduction_amount:,.0f}원)"
            
            usage_info = f"{percent_used:.1f}% 사용"
            used_amount = deduction_amount
        else:
            if ticket_type == "기간권":
                used_amount = used_days * daily_rate
            elif ticket_type == "노블레스석":
                used_amount = used_days * noble_rate
            elif ticket_type == "시간권":
                used_amount = hours_used * hourly_rate
            refund_amount = max(ticket_price - used_amount, 0)
            usage_info = f"{used_days}일 사용" if ticket_type in ["기간권", "노블레스석"] else f"{hours_used}시간 사용"
            deduction_detail = f"{used_days}일 × {daily_rate:,}원" if ticket_type == "기간권" else f"{used_days}일 × {noble_rate:,}원 (노블레스석 1일 요금)" if ticket_type == "노블레스석" else f"{hours_used}시간 × {hourly_rate:,}원"
        
        # 위약금 계산 (결제금액 기준)
        penalty_rate_value = int(penalty_rate.strip("%")) / 100  # 위약금 비율 (10% → 0.1)
        penalty_amount = ticket_price * penalty_rate_value  # 위약금 금액 (결제금액 기준)
        final_refund_amount = max(refund_amount - penalty_amount, 0)  # 최종 환불 금액 (음수 방지)
        
        # 한국 시간대 (KST)로 현재 시간 설정
        kst = pytz.timezone('Asia/Seoul')
        current_time_kst = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
        
        # 환불 내역서 구성
        refund_detail = f"""
        [멘토즈 스터디카페 환불 내역서]
        =============================================
        ■ 지   점 : {branch}
        ■ 연락처 : {phone}
        ■ 발급일 : {current_time_kst}
        ---------------------------------------------
        [구 매 정 보]
        - 이용권 종류 : {formatted_ticket_type}
        - 결 제 일 자 : {purchase_date.strftime('%Y-%m-%d')}
        - 결제 금액 : {ticket_price:,}원
        - 유효 기간 : {valid_period}
        ---------------------------------------------
        [환 불 내역]
        ▣ 사용량 : {usage_info}
        ▣ 공제 금액 : -{used_amount:,}원 ({deduction_detail})
        ▣ 위약금 : -{penalty_amount:,.0f}원 ({penalty_rate} 위약금)
        ▣ 환불 금액 : {int(final_refund_amount):,}원
        ▶ 회원 정보 : {phone} (고객 전화번호 기준)
        =============================================
        ※ 유의사항
        - 본 내역서는 발급일 기준으로 유효합니다.
        - 결제일자로 부터 30일이 지난 결제건은 위약금이 추가로 발생할 수 있습니다.
        - 환불 처리에는 최대 3~5영업일이 소요될 수 있습니다.
        """
        
        # 환불 내역서 출력
        st.text_area("📄 환불 내역서 (Ctrl+C로 복사 가능)", refund_detail.strip(), height=400)
        st.download_button("📥 환불 내역서 다운로드", refund_detail.strip(), file_name="refund_details.txt")
  
if __name__ == "__main__":
    main()