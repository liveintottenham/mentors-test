import streamlit as st
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# Google 스프레드시트 인증 설정
def authenticate_google_sheets():
    """GitHub Secrets에서 Service Account JSON을 로드"""
    credentials_json = os.getenv("GSPREAD_API_KEY")  # GitHub Secrets에서 JSON 문자열 직접 가져오기
    
    if not credentials_json:
        raise Exception("🚨 GitHub Secrets에 GSPREAD_API_KEY가 설정되지 않았습니다.")
    
    try:
        credentials_info = json.loads(credentials_json)  # JSON 문자열 파싱
        credentials = Credentials.from_service_account_info(credentials_info)
        return gspread.authorize(credentials)
    except json.JSONDecodeError:
        raise Exception("🚨 JSON 형식이 잘못되었습니다. Secrets 설정을 확인하세요.")

# 스프레드시트 데이터 불러오기
def load_spreadsheet_data():
    try:
        client = authenticate_google_sheets()
        spreadsheet = client.open("멘토즈 지점 정보")  # 스프레드시트 이름
        sheet = spreadsheet.worksheet("시트1")  # 시트 이름
        return sheet.get_all_records()  # 데이터 반환
    except Exception as e:
        st.error(f"🚨 데이터를 불러오는 중 오류가 발생했습니다: {e}")
        return []

# Streamlit UI
def main():
    st.title("📊 멘토즈 지점 정보 관리")
    
    # 데이터 불러오기
    data = load_spreadsheet_data()
    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.warning("데이터를 불러올 수 없습니다.")

if __name__ == "__main__":
    main()