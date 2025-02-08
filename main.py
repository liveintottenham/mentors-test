import streamlit as st

st.title("🔑 GitHub Secrets 테스트")

gspread_api_key = st.secrets["GSPREAD_API_KEY"]

if gspread_api_key:
    st.success("✅ GSPREAD_API_KEY가 정상적으로 로드되었습니다!")
    st.write(f"🔍 Base64 길이: {len(gspread_api_key)}")
else:
    st.error("🚨 GitHub Secrets에 GSPREAD_API_KEY가 설정되지 않았습니다.")