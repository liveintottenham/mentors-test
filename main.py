import os
import base64
import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ✅ API Key 로드 함수 (환경 변수 지원)
def authenticate_google_sheets():
    """GitHub Secrets 또는 환경 변수에서 Service Account JSON을 로드"""
    gspread_api_key = st.secrets.get("GSPREAD_API_KEY") or os.getenv("GSPREAD_API_KEY")

    if not gspread_api_key:
        raise Exception("🚨 API Key를 찾을 수 없습니다. GitHub Secrets 또는 환경 변수를 확인하세요.")

    try:
        decoded_json = base64.b64decode(gspread_api_key).decode()
        credentials_info = json.loads(decoded_json)
        credentials = Credentials.from_service_account_info(credentials_info)
        return gspread.authorize(credentials)
    except Exception as e:
        raise Exception(f"🚨 JSON 디코딩 실패: {str(e)}")
