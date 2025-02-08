import os
import base64
import json
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ✅ 강제 환경 변수 로드 방식
def authenticate_google_sheets():
    gspread_api_key = os.environ.get("GSPREAD_API_KEY")  # os.getenv() 대신 os.environ.get() 사용

    if not gspread_api_key:
        raise Exception("🚨 환경 변수에서 API Key를 찾을 수 없습니다.")

    try:
        decoded_json = base64.b64decode(gspread_api_key).decode()
        credentials_info = json.loads(decoded_json)
        credentials = Credentials.from_service_account_info(credentials_info)
        return gspread.authorize(credentials)
    except Exception as e:
        raise Exception(f"🚨 JSON 디코딩 실패: {str(e)}")

authenticate_google_sheets()  # 테스트 실행
