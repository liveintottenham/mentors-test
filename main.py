import streamlit as st
from datetime import datetime, timedelta

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    st.markdown("## 🔐 접근 제한")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    if st.button("로그인"):
        if password == "1234":  # ✅ 여기에 원하는 비밀번호 설정
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다!")
    
    return st.session_state.authenticated

def main():
    if not check_password():
        return  # 인증되지 않으면 실행 안 됨
    
    st.set_page_config(page_title="멘토즈 가맹관리부 ", page_icon="📚", layout="wide", initial_sidebar_state="expanded")
    
    st.sidebar.markdown(
        """
        <style>
        .sidebar-title {
            font-size: 24px;
            font-weight: bold;
            text-align: center;
            color: #ffffff;
            margin-bottom: 20px;
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
    
    st.sidebar.markdown('<p class="sidebar-title">📌 메뉴</p>', unsafe_allow_html=True)
    
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
    locker_number = st.text_input("사물함 번호를 입력하세요")
    locker_password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if st.button("마스터키 안내 보기"):
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

def restore_checkout_page():
    st.title("🛠️ 퇴실 미처리 복구")
    checkout_date = st.text_input("퇴실 일자 (YYYYMMDD)")
    checkout_time = st.text_input("퇴실 시간 (HHMM)")
    
    if st.button("미처리 시간 계산"):
        try:
            checkout_datetime = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y%m%d %H%M")
            now = datetime.now()
            if checkout_datetime > now:
                st.error("❌ 퇴실 시간이 미래일 수 없습니다!")
                return
            lost_time = now - checkout_datetime
            lost_minutes = int(lost_time.total_seconds() // 60)
            lost_hours = lost_minutes // 60
            remaining_minutes = lost_minutes % 60
            extra_fee = (lost_minutes // 30) * 1000
            st.success(f"📅 미처리 기간: {checkout_datetime.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}")
            st.success(f"⏳ 미처리 시간: {lost_hours}시간 {remaining_minutes}분")
            st.success(f"💰 초과 요금: {extra_fee:,}원 (30분당 1,000원)")
        except ValueError:
            st.error("❌ 올바른 날짜 및 시간 형식을 입력하세요!")

def refund_calculator_page():
    st.title("💰 이용권 환불 계산")
    branch = st.text_input("지점명")
    phone = st.text_input("전화번호")
    ticket_type = st.radio("이용권 종류", ["기간권", "시간권", "노블레스석"])
    policy = st.radio("환불 규정", ["일반", "% 규정"])
    
    ticket_price = st.number_input("결제 금액 (원)", min_value=0)
    purchase_date = st.date_input("결제일")
    refund_date = st.date_input("환불 요청일")
    
    days_given = st.number_input("전체 부여 기간 [일] (기간권/노블레스석)", min_value=1) if ticket_type in ["기간권", "노블레스석"] else None
    weeks_given = st.number_input("유효 기간 [주] (시간권)", min_value=1) if ticket_type == "시간권" else None
    hours_used = st.number_input("사용 시간 (시간권)", min_value=0) if ticket_type == "시간권" else None
    total_hours = st.number_input("전체 부여 시간 (시간권)", min_value=1) if ticket_type == "시간권" else None
    noble_rate = st.number_input("노블레스석 1일 요금 (원)", min_value=0) if ticket_type == "노블레스석" else None
    
    formatted_ticket_type = f"{ticket_type} ({days_given}일)" if ticket_type != "시간권" else f"{ticket_type} ({total_hours}시간)"
    
    if ticket_type == "시간권":
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(weeks=weeks_given)).strftime('%Y-%m-%d')}"
    else:
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(days=days_given-1)).strftime('%Y-%m-%d')}" if days_given else "정보 없음"
    
    if st.button("환불 금액 계산"):
        used_days = (refund_date - purchase_date).days + 1
        daily_rate = 11000
        hourly_rate = 2000
        used_amount = 0
        
        if policy == "% 규정":
            percent_used = (used_days / days_given) * 100 if ticket_type in ["기간권", "노블레스석"] else (hours_used / total_hours) * 100
            
            if percent_used <= 25:
                refund_amount = ticket_price * 0.5
                deduction_amount = ticket_price * 0.5
                deduction_detail = f"0~25% 환불 구간 : 결제금액의 50% 환불 ({deduction_amount:,.0f}원)"
            elif percent_used <= 50:
                refund_amount = ticket_price * 0.25
                deduction_amount = ticket_price * 0.75
                deduction_detail = f"26~50% 환불 구간 : 결제금액의 25% 환불 ({deduction_amount:,.0f}원)"
            else:
                refund_amount = 0
                deduction_amount = ticket_price
                deduction_detail = f"50% 초과 사용 구간 : 환불 불가 ({deduction_amount:,.0f}원)"
            
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
        
        refund_detail = f"""
        [멘토즈 스터디카페 환불 내역서]
        =============================================
        ■ 지   점 : {branch}
        ■ 연락처 : {phone}
        ■ 발급일 : {datetime.now().strftime('%Y-%m-%d %H:%M')}
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
        ▣ 환불 금액 : {int(refund_amount):,}원
        ▶ 회원 정보 : {phone} (고객 전화번호 기준)
        =============================================
        ※ 유의사항
        - 본 내역서는 발급일 기준으로 유효합니다.
        - 환불 처리에는 최대 3~5영업일이 소요될 수 있습니다.
        """
        
        st.text_area("📄 환불 내역서 (Ctrl+C로 복사 가능)", refund_detail.strip(), height=350)
        st.download_button("📥 환불 내역서 다운로드", refund_detail.strip(), file_name="refund_details.txt")

  
    
if __name__ == "__main__":
    main()