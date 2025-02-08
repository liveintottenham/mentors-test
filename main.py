import os

# 환경 변수 확인
gspread_api_key = os.getenv("GSPREAD_API_KEY")

if gspread_api_key:
    print("✅ GSPREAD_API_KEY가 정상적으로 로드되었습니다.")
    print("🔍 Base64 길이:", len(gspread_api_key))  # Base64 길이 확인
else:
    raise Exception("🚨 GitHub Secrets에 `GSPREAD_API_KEY`가 설정되지 않았습니다.")
