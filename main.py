import base64
import json

def decode_json_key(encoded_key):
    decoded_json = base64.b64decode(encoded_key).decode()
    credentials_info = json.loads(decoded_json)
    return credentials_info

# 테스트용 Base64 인코딩된 JSON 키
encoded_key = os.getenv("GSPREAD_API_KEY")
if encoded_key:
    try:
        credentials_info = decode_json_key(encoded_key)
        print("JSON 키 파일 디코딩 성공!")
    except Exception as e:
        print(f"JSON 키 파일 디코딩 실패: {e}")
else:
    print("환경 변수 GSPREAD_API_KEY를 찾을 수 없습니다.")