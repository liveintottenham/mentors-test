import streamlit as st
from datetime import datetime, timedelta

def main():
    st.set_page_config(page_title="멘토즈 스터디카페 시스템", page_icon="📚", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background-color: #f5f7fa; }
        .title-text { text-align: center; font-size: 32px; font-weight: bold; color: #2c3e50; }
        .sub-title { text-align: center; font-size: 18px; color: #7f8c8d; }
        .section-header { font-size: 24px; font-weight: bold; color: #2980b9; }
        .button-container { display: flex; justify-content: center; gap: 20px; }
        .button-container button { width: 250px; height: 60px; font-size: 18px; }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<p class="title-text">멘토즈 스터디카페 시스템</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">사물함 마스터키 안내 · 퇴실 미처리 복구 · 환불 계산</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔑 사물함 마스터키 안내"):
            locker_masterkey_page()
    with col2:
        if st.button("🔄 퇴실 미처리 복구"):
            restore_checkout_page()
    with col3:
        if st.button("💰 이용권 환불 계산"):
            refund_calculator_page()

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
    st.subheader("🔄 퇴실 미처리 복구")
    user_id = st.text_input("사용자 ID (전화번호)")
    visit_date = st.date_input("방문 날짜")
    
    if st.button("복구 요청하기"):
        if not user_id:
            st.error("❌ 사용자 ID를 입력하세요!")
        else:
            restore_info = (
                f"✅ 퇴실 미처리 복구 요청 완료!\n\n"
                f"👤 사용자 ID: {user_id}\n"
                f"📅 방문 날짜: {visit_date.strftime('%Y-%m-%d')}\n\n"
                "⚠️ 복구 요청이 접수되었습니다.\n"
                "운영진 확인 후 24시간 이내에 처리됩니다."
            )
            st.text_area("📌 복구 요청 내역", restore_info, height=200)

def refund_calculator_page():
    st.subheader("💰 이용권 환불 계산")
    st.write("이용권 환불 금액을 계산할 수 있습니다.")
    
    # 기존 환불 계산 코드 유지
    
if __name__ == "__main__":
    main()
