import os

gspread_api_key = os.getenv("GSPREAD_API_KEY")

if gspread_api_key:
    print("✅ 환경 변수 GSPREAD_API_KEY가 정상적으로 로드되었습니다.")
else:
    print("🚨 환경 변수 GSPREAD_API_KEY를 찾을 수 없습니다. GitHub Secrets 설정을 확인하세요.")
