import streamlit as st
from datetime import datetime, timedelta

def refund_calculator_page():
    st.title("💰 이용권 환불 계산")
    branch = st.text_input("지점명")
    phone = st.text_input("전화번호")
    ticket_type = st.radio("이용권 종류", ["기간권", "시간권", "노블레스석"])
    policy = st.radio("환불 규정", ["일반", "% 규정"])
    
    ticket_price = st.number_input("결제 금액 (원)", min_value=0)
    purchase_date = st.date_input("결제일")
    refund_date = st.date_input("환불 요청일")
    
    days_given = st.number_input("부여된 일수 (기간권/노블레스석)", min_value=1) if ticket_type in ["기간권", "노블레스석"] else None
    weeks_given = st.number_input("유효 기간 (주) (시간권)", min_value=1) if ticket_type == "시간권" else None
    hours_used = st.number_input("사용한 시간 (시간권)", min_value=0) if ticket_type == "시간권" else None
    total_hours = st.number_input("총 이용 가능 시간 (시간권)", min_value=1) if ticket_type == "시간권" else None
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
        
        st.text_area("📄 환불 내역서", refund_detail.strip(), height=350)
        copy_script = f'<button onclick="navigator.clipboard.writeText(`{refund_detail.strip()}`);alert(\'🔔 클립보드에 복사되었습니다!\')">📋 클립보드에 복사</button>'
        st.markdown(copy_script, unsafe_allow_html=True)

st.sidebar.title("📌 메뉴")
page = st.sidebar.radio("페이지 선택", ["사물함 마스터키", "환불 계산기", "퇴실 미처리 복구"])

if page == "사물함 마스터키":
    locker_masterkey_page()
elif page == "환불 계산기":
    refund_calculator_page()
elif page == "퇴실 미처리 복구":
    restore_checkout_page()