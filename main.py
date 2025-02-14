import streamlit as st
from datetime import datetime, timedelta
import pytz, gspread, random, string, os, json
from google.oauth2.service_account import Credentials
import pandas as pd
from streamlit.components.v1 import html  # HTML/JS 사용
import plotly.express as px
import folium,requests
from streamlit_folium import folium_static 


# ✅ 페이지 설정
st.set_page_config(
    page_title="멘토즈 가맹관리부 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 야간모드 비활성화
st.markdown(
    """
    <style>
        /* 라이트 모드 강제 적용 */
        body {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* 다크 모드의 스타일을 강제로 변경 */
        .dark .stApp {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

        /* 다크 모드에서 배경 색상 등을 흰색으로 설정 */
        .dark .stTextInput input, .dark .stButton button, .dark .stExpander {
            background-color: #ffffff !important;
            color: #000000 !important;
        }

    </style>
    """, unsafe_allow_html=True
)

# ✅ Pretendard 폰트 적용 (Google Fonts)
st.markdown(
    """
    <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/Pretendard/dist/web/static/pretendard.css');

        * {
            font-family: 'Pretendard', sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# 한국 시간(KST) 설정
kst = pytz.timezone('Asia/Seoul')
now = datetime.now(kst)

# 시간 형식으로 출력
st.write(f'{now.strftime("%Y-%m-%d %H:%M")} [user]')

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    st.markdown("## 🔐 접근 제한")
    
    # ✅ 엔터 키 처리
    container = st.container()
    password = container.text_input(
        "비밀번호를 입력하세요 (Enter로 제출)", 
        type="password", 
        key="login_password",
        on_change=lambda: st.session_state.update(login_attempted=True)
    )
    
    # ✅ 버튼 또는 엔터 키로 제출
    if container.button("로그인") or st.session_state.get("login_attempted", False):
        if password == "1234":
            st.session_state.authenticated = True
            st.session_state.login_attempted = False  # 초기화
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다!")
            st.session_state.login_attempted = False  # 초기화
    
    return st.session_state.authenticated

# ✅ Google Sheets 인증 함수
def authenticate_google_sheets():
    """GitHub Secrets에서 Service Account JSON을 로드"""
    credentials_json = os.getenv("GSPREAD_API_KEY")
    
    if not credentials_json:
        raise Exception("🚨 GitHub Secrets에 GSPREAD_API_KEY가 설정되지 않았습니다.")
    
    try:
        # ✅ 최신 OAuth 범위 설정
        scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        # ✅ JSON 키 파싱 및 인증
        credentials_info = json.loads(credentials_json)
        credentials = Credentials.from_service_account_info(credentials_info, scopes=scope)
        return gspread.authorize(credentials)
    
    except json.JSONDecodeError:
        raise Exception("🚨 JSON 형식 오류: Secrets에 저장된 키가 유효하지 않습니다.")
    except Exception as e:
        raise Exception(f"🚨 인증 실패: {str(e)}")


@st.cache_data(ttl=5)
def get_real_time_data():
    try:
        client = authenticate_google_sheets()
        spreadsheet = client.open("멘토즈 지점 정보")
        sheet = spreadsheet.worksheet("시트1")
        
        # ✅ 모든 데이터를 텍스트로 가져오기
        data = sheet.get_all_values()  # 모든 데이터를 텍스트로 가져옴
        df = pd.DataFrame(data[1:], columns=data[0])  # 첫 번째 행을 컬럼명으로 사용

        # ✅ 컬럼명 정규화 (공백 제거 및 대소문자 통일)
        df.columns = df.columns.str.strip().str.replace(" ", "")
        
        # ✅ 필수 컬럼 존재 여부 확인
        required_columns = ["지점명", "사물함ID", "사물함PWD", "ID", "PWD", 
                   "지점카카오톡채널", "스터디룸여부", "주차여부", "노트북/프린트"]
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"구글 시트에 '{col}' 컬럼이 없습니다. 시트 구조를 확인해주세요.")
        
        # ✅ 모든 0 패딩 제거 (사물함ID, 사물함PWD)
        df["사물함ID"] = df["사물함ID"].astype(str).str.strip()
        df["사물함PWD"] = df["사물함PWD"].astype(str).str.strip()

        # ✅ ID, PWD 컬럼: 텍스트 형식으로 강제 변환 (앞의 0 유지, 빈 값은 공백 처리)
        df["ID"] = df["ID"].apply(lambda x: str(x).strip() if x else "")
        df["PWD"] = df["PWD"].apply(lambda x: str(x).strip() if x else "")

        return df

    except Exception as e:
        st.error(f"📊 데이터 조회 실패: {str(e)}")
        return pd.DataFrame()  # 빈 데이터프레임 반환


# ✅ 데이터 업데이트 함수
def update_sheet(new_data):
    try:
        client = authenticate_google_sheets()
        spreadsheet = client.open("멘토즈 지점 정보")  # Google Sheets 문서 이름
        sheet = spreadsheet.worksheet("시트1")  # 시트 이름

        # ✅ 헤더 포함 전체 데이터 업데이트
        sheet.clear()
        sheet.update(
            [new_data.columns.tolist()] + 
            new_data.astype(str).values.tolist()
        )
        st.cache_data.clear()  # 캐시 초기화
        
    except gspread.exceptions.APIError as e:
        st.error(f"📤 업데이트 실패: Google API 오류 ({str(e)})")
    except Exception as e:
        st.error(f"📤 업데이트 실패: {str(e)}")

# ✅ 고유한 ID 생성 함수
def generate_random_id():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# ✅ Streamlit 세션 상태 초기화
if "random_id" not in st.session_state:
    st.session_state.random_id = generate_random_id()

if "can_edit" not in st.session_state:
    st.session_state.can_edit = False

if "edited_data" not in st.session_state:
    st.session_state.edited_data = None

if "new_row" not in st.session_state:
    st.session_state.new_row = {}

if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# ✅ Streamlit UI 시작
def load_and_display_spreadsheet_data():
    st.title("📊 스프레드시트 데이터 관리")

    # ✅ 실시간 데이터 가져오기``
    df = get_real_time_data()

    # ✅ 지점명 검색 필드 추가
    branch_name = st.text_input("🔍 지점명 입력 후 엔터 (예시: '부산연산점' -> '연산')", key=f"branch_search_{st.session_state.random_id}")

    # ✅ 검색된 지점명에 맞춰 데이터 필터링
    filtered_df = df[df["지점명"].str.contains(branch_name, case=False, na=False)] if branch_name else df

    # ✅ Streamlit 데이터 표시 (읽기 전용)
    st.subheader("📊 지점 데이터 확인")
    if st.session_state.can_edit:
        # ✅ 수정 가능 상태에서 데이터 편집 활성화
        edited_df = st.data_editor(
            filtered_df, 
            num_rows="dynamic", 
            use_container_width=True, 
            key=f"editor_{st.session_state.random_id}"
        )
        st.session_state.edited_data = edited_df.values.tolist()  # ✅ 수정된 데이터 저장
    else:
        # ✅ 수정 불가능한 상태에서 표가 꽉 차도록 유지
        st.dataframe(filtered_df, use_container_width=True)

    # ✅ 버튼 UI (수평 배치)
    button_col1, button_col2, button_col3 = st.columns(3)

    # ✅ 지점 정보 추가 버튼
    with button_col1:
        if st.button("📌 지점 정보 추가", key=f"add_branch_{st.session_state.random_id}"):
            st.session_state.show_add_form = True  # 입력창 표시 상태

    # ✅ 입력창 표시
    if st.session_state.show_add_form:
        with st.expander("📝 새 지점 정보 추가", expanded=True):
            new_row = {}
            for col in df.columns:
                # ✅ '마스터키 PWD'는 문자열로만 입력받기
                if col == "마스터키 PWD":
                    new_row[col] = st.text_input(
                        f"{col} 입력",
                        value=st.session_state.new_row.get(col, ""),  # 기존 입력값 유지
                        key=f"new_{col}_{st.session_state.random_id}"
                    )
                else:
                    # 다른 열의 데이터 타입에 맞게 처리
                    if df[col].dtype == "int64":
                        new_row[col] = st.number_input(
                            f"{col} 입력",
                            value=st.session_state.new_row.get(col, 0),  # 기존 입력값 유지
                            key=f"new_{col}_{st.session_state.random_id}"
                        )
                    elif df[col].dtype == "float64":
                        new_row[col] = st.number_input(
                            f"{col} 입력",
                            value=st.session_state.new_row.get(col, 0.0),  # 기존 입력값 유지
                            key=f"new_{col}_{st.session_state.random_id}",
                            format="%.2f"
                        )
                    else:
                        new_row[col] = st.text_input(
                            f"{col} 입력",
                            value=st.session_state.new_row.get(col, ""),  # 기존 입력값 유지
                            key=f"new_{col}_{st.session_state.random_id}"
                        )
            
            # ✅ 입력값을 세션 상태에 저장
            st.session_state.new_row = new_row

            if st.button("✅ 새 데이터 추가", key=f"add_data_{st.session_state.random_id}"):
                try:
                    # ✅ 필수 필드 검증
                    if any(value == "" or value is None for value in new_row.values()):
                        st.error("🚨 모든 필드를 입력해야 합니다!")
                    else:
                        # ✅ '마스터키 PWD'를 문자열로 강제 변환
                        new_row["마스터키 PWD"] = str(new_row["마스터키 PWD"])
                        
                        # ✅ DataFrame에 새로운 행 추가
                        new_df = pd.DataFrame([new_row])
                        updated_df = pd.concat([df, new_df], ignore_index=True)
                        update_sheet(updated_df)  # 데이터 업데이트 함수 호출
                        st.success("✅ 데이터가 성공적으로 추가되었습니다!")
                        
                        # ✅ 입력창 초기화
                        st.session_state.show_add_form = False
                        st.session_state.new_row = {}
                        st.rerun()
                except Exception as e:
                    st.error(f"🚨 에러 발생: {str(e)}")

    # ✅ 수정하기 버튼
    with button_col2:
        if st.button("✏️ 수정하기", key=f"edit_button_{st.session_state.random_id}"):
            st.session_state.can_edit = True  # ✅ 수정 모드 활성화

    # ✅ 모든 변경사항 저장 버튼
    with button_col3:
        if st.button("💾 모든 변경사항 저장", key=f"save_button_{st.session_state.random_id}"):
            try:
                if st.session_state.can_edit and st.session_state.edited_data is not None:
                    edited_df = pd.DataFrame(st.session_state.edited_data, columns=df.columns)
                    update_sheet(edited_df)  # ✅ 수정된 데이터 반영
                    st.success("✅ 변경사항이 저장되었습니다! 새로고침 없이 즉시 반영됩니다.")
                    st.session_state.can_edit = False
                    st.session_state.edited_data = None
                else:
                    st.warning("⚠️ 수정된 데이터가 없습니다.")
            except Exception as e:
                st.error(f"🚨 저장 실패: {e}")

    # ✅ 데이터 삭제 기능
    with st.expander("⚠️ 데이터 삭제"):
        row_num = st.number_input("삭제할 행 번호", min_value=2, max_value=len(df)+1, key=f"delete_row_{st.session_state.random_id}")
        if st.button("🗑️ 선택한 행 삭제", key=f"delete_button_{st.session_state.random_id}"):
            try:
                client = authenticate_google_sheets()
                spreadsheet = client.open("멘토즈 지점 정보")
                sheet = spreadsheet.worksheet("시트1")
                sheet.delete_rows(row_num)
                st.cache_data.clear()  # ✅ 캐시 초기화
                st.success(f"✅ {row_num}번 행이 삭제되었습니다!")
                st.rerun()
            except Exception as e:
                st.error(f"🚨 삭제 실패: {e}")

# ✅ Google Sheets 인증 함수 (end)

def get_address_coordinates(address):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {st.secrets['KAKAO']['REST_API_KEY']}"}
    params = {"query": address}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
        result = response.json()
        
        if result["documents"]:
            y = result["documents"][0]["y"]  # 위도
            x = result["documents"][0]["x"]  # 경도
            return y, x
        else:
            st.error("⚠️ 해당 주소를 찾을 수 없습니다.")
            return None, None
    except requests.exceptions.RequestException as e:
        st.error(f"🚨 API 호출 실패: {str(e)}")
        return None, None

# ✅ 지점 정보 확인 페이지

def branch_info_page():
    st.title("🏢 지점 정보 확인")
    df = get_real_time_data()
    
    required_columns = ["지점명", "사물함ID", "사물함PWD", "ID", "PWD", 
                        "지점카카오톡채널", "스터디룸여부", "특이사항", "주차여부", "노트북/프린트", "주소"]
    for col in required_columns:
        if col not in df.columns:
            st.error(f"구글 시트에 '{col}' 컬럼이 없습니다. 시트 구조를 확인해주세요.")
            return

    # 지점명 검색 입력
    search_term = st.text_input("🔍 지점명 검색 (예시: '부산연산점' -> '연산')", key="branch_info_search")
    
    if search_term:
        filtered = df[df["지점명"].str.contains(search_term, case=False, na=False)]
        filtered = filtered.drop_duplicates(subset=["지점명"])
    else:
        filtered = pd.DataFrame()

    if not filtered.empty:
        branch_names = filtered["지점명"].tolist()
        selected_branch = st.selectbox("지점 선택", branch_names, key="branch_select")
        
        branch_data = filtered[filtered["지점명"] == selected_branch].iloc[0]
        id_val = str(branch_data["ID"]).strip()
        pw_val = str(branch_data["PWD"]).strip()
        channel_info = str(branch_data.get("지점카카오톡채널", "N/A")).strip()
        special_notes = str(branch_data.get("특이사항", "")).strip()
        parking = str(branch_data.get("주차여부", "N/A")).strip()
        laptop_printer = str(branch_data.get("노트북/프린트", "N/A")).strip()
        address = str(branch_data.get("주소", "N/A")).strip()
        study_room = str(branch_data.get("스터디룸여부", "N/A")).strip()

        # 상단 2단 레이아웃
        col1, col2 = st.columns(2)

        # 왼쪽: 아이디와 비밀번호
        with col1:
            st.subheader("🖥️ 계정 정보")
            if id_val != "" and pw_val != "":
                st.markdown("**아이디**")
                st.code(id_val, language="text")
                st.markdown("**비밀번호**")
                st.text_input("비밀번호", value=pw_val, type="password", disabled=True)
                
                # 관리자 페이지 버튼
                st.markdown("---")
                st.markdown("**관리자 페이지**")
                if st.button("🖥️ 제로아이즈 관리자 페이지"):
                    open_link_in_new_tab("https://mentors.mooin.kr/login")
                if st.button("📱 컴앤패스 관리자 앱 열기"):
                    open_link_in_new_tab("https://mg.smonster.kr/")
            else:
                st.warning("아이디와 비밀번호 정보가 없습니다.")

        # 오른쪽: 부가 정보
        with col2:
                st.subheader("📌 지점 상세 정보")
    
                # ✅ 지점 채널 (기존 코드 유지)
                with st.expander("💬 지점 채널", expanded=True):
                    if channel_info != "N/A":
                        st.write(f"카카오톡 채널: {channel_info}")
                        
                        # ✅ 지점채널 안내문 생성 버튼 추가
                        if st.button("📩 지점채널 안내문 생성", key="generate_channel_message"):
                            message = f"""
                            안녕하세요, 멘토즈스터디카페 운영본부입니다.
                            유선상 전달드린 카카오톡 지점 채널 안내드립니다.

                            {channel_info}
                            ▶ 카카오톡 지점 채널 [ 멘토즈 {selected_branch} ]

                            ※ 상담 가능 시간 이외라도 긴급 건의 경우 점주님이 확인 후 답변 주시고 있으며, 
                            전화 문의는 불가한 점 양해 부탁드립니다.
                            """
                            st.code(message)
                    else:
                        st.warning("지점 채널 정보가 없습니다.")
    
                # 노트북/프린트 섹션 수정
                with st.expander("💻 노트북/프린트", expanded=True):
                    st.markdown(f"""
                    <div style="font-size:16px; font-weight:600; color:#2c3e50; 
                                margin: 15px 0; line-height:1.6;">
                        {laptop_printer}
                    </div>
                    """, unsafe_allow_html=True)
    
                # ✅ 특이사항 (빨간색 강조)
                if special_notes and special_notes != "":
                    with st.expander("🚨 특이사항", expanded=True):
                        st.markdown(f"""
                        <div style="font-size:16px; color:#e74c3c; font-weight:600; white-space: pre-line;">
                            {special_notes}
                        </div>
                        """, unsafe_allow_html=True)
    
                # 주차여부 섹션 수정
                with st.expander("🚗 주차 여부", expanded=True):
                    st.markdown(f"""
                    <div style="font-size:16px; color:#2ecc71; font-weight:600; 
                                margin: 15px 0; line-height:1.6;">
                        {parking}
                    </div>
                    """, unsafe_allow_html=True)
                
                # ✅ 스터디룸 정보
                study_room = str(branch_data.get("스터디룸여부", "N/A")).strip()
                with st.expander("📚 스터디룸 여부", expanded=True):
                    st.write(f"{study_room}")

        # 하단: 지점 위치 지도 (1단 레이아웃)
        st.subheader("📍 지점 위치")
        st.markdown(f"**멘토즈** {selected_branch}")
        st.markdown(f"**주소**: {address}")

        # ✅ REST API를 사용하여 주소를 좌표로 변환
        if address != "N/A":
            y, x = get_address_coordinates(address)
            if y and x:
                # ✅ 지도 표시
                map_html = f"""
                <meta http-equiv="Content-Security-Policy" content="upgrade-insecure-requests">
                <div id="map" style="width:100%;height:400px;border-radius:12px;margin:0 auto;"></div>
                <script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={st.secrets['KAKAO']['MAP_API_KEY']}&libraries=services"></script>
                <script>
                    var mapContainer = document.getElementById('map');
                    var mapOption = {{
                        center: new kakao.maps.LatLng({y}, {x}), // 변환된 좌표 사용
                        level: 3
                    }};
                    var map = new kakao.maps.Map(mapContainer, mapOption);

                    // 마커 생성
                    var marker = new kakao.maps.Marker({{
                        map: map,
                        position: new kakao.maps.LatLng({y}, {x})
                    }});

                    // 인포윈도우 생성
                    var infowindow = new kakao.maps.InfoWindow({{
                        content: '<div style="padding:10px;font-size:14px;">{selected_branch}</div>'
                    }});
                    infowindow.open(map, marker);
                </script>
                """
                st.components.v1.html(map_html, height=420)
            else:
                st.error("⚠️ 주소를 좌표로 변환할 수 없습니다.")
        else:
            st.warning("⚠️ 주소 정보가 없습니다.")
        

# ✅ 새 탭에서 링크 열기 함수 (JavaScript 사용)
def open_link_in_new_tab(url):
    # JavaScript 실행 방식 개선
    js = f"""<script>window.open("{url}", "_blank");</script>"""
    html(js, height=0, width=0)



# ✅ 홈 페이지
def home_page():
    st.markdown(
    """
    <style>
    /* 카드 디자인 업그레이드 */
    .card {
        background: linear-gradient(145deg, #ffffff, #f8f9fa);
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s, box-shadow 0.3s;
        border: 1px solid #e0e0e0;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
    }

    /* 타이틀 디자인 */
    .section-title {
        font-size: 24px !important;
        color: #2c3e50 !important;
        border-left: 4px solid #2ecc71;
        padding-left: 15px;
        margin: 25px 0 !important;
    }

    /* 그래프 색상 통일 */
    .stPlotlyChart {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)


    # ✅ 공지사항 데이터
    notices = [
        {"날짜": "2025-02-14", "제목": "환불 영수증 발급 시스템 점검중", "링크": "https://example.com"},
        {"날짜": "2025-02-08", "제목": "멘토즈 가맹관리부 시스템 오픈 ", "링크": "https://example.com"},
    ]

    # ✅ 최근 오픈 지점 데이터
    recent_openings = [
        {"날짜": "2025-02-27", "지점명": "멘토즈 장전래미안점"},
        {"날짜": "2025-02-24", "지점명": "멘토즈 경성대점"},
        {"날짜": "2025-02-01", "지점명": "멘토즈 당산푸르지오점"},
    ]

    # ✅ 공지사항 & 최근 오픈 지점을 반반으로 나누어 배치
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-title">📢 최신 공지사항</div>', unsafe_allow_html=True)
        for notice in notices:
            st.markdown(
                f"""
                <div class="card">
                    <div style="color: #2ecc71; font-size: 12px;">{notice['날짜']}</div>
                    <div style="font-size: 16px; font-weight: 600; margin: 10px 0;">{notice['제목']}</div>
                    <a href="{notice['링크']}" target="_blank" style="text-decoration: none; color: #3498db;">👉 바로가기</a>
                </div>
                """, 
                unsafe_allow_html=True
            )

    with col2:
        st.subheader("🏢 최근 오픈 지점")
        for opening in recent_openings:
            st.markdown(
                f"""
                <div class="card">
                    <h4>📅 {opening['날짜']}</h4>
                    <p><strong>{opening['지점명']}</strong></p>
                </div>
                """, unsafe_allow_html=True
            )

    st.markdown("---")

    # ✅ 최근 오픈 지점 캘린더 (그래프)
    st.subheader("📅 최근 오픈 지점 일정")

    # ✅ 데이터 변환 (날짜 순서 정렬)
    df_openings = pd.DataFrame(recent_openings)
    df_openings["날짜"] = pd.to_datetime(df_openings["날짜"])
    df_openings = df_openings.sort_values("날짜")

    # ✅ 캘린더 그래프
    fig_calendar = px.scatter(df_openings, x="날짜", y="지점명", size=[10] * len(df_openings),
                              color="지점명", title="최근 오픈 지점 캘린더",
                              labels={"날짜": "오픈 날짜", "지점명": "지점명"})
    st.plotly_chart(fig_calendar, use_container_width=True)

    # ✅ 최근 오픈 지점 트렌드 그래프
    st.subheader("📊 최근 오픈 지점 증가 추세")

    # ✅ 오픈 지점 개수 그래프 (날짜별 카운트)
    df_openings["오픈 개수"] = 1
    df_trend = df_openings.groupby("날짜").sum().reset_index()

    fig_trend = px.line(df_trend, x="날짜", y="오픈 개수", markers=True, title="최근 오픈 지점 증가 추세",
                        labels={"날짜": "오픈 날짜", "오픈 개수": "오픈된 지점 수"})
    st.plotly_chart(fig_trend, use_container_width=True)

def locker_masterkey_page():
    st.title("🔑 사물함 마스터키 안내")
    df = get_real_time_data()
    
    # ✅ 지점 검색 로직
    search_term = st.text_input("🔍 지점명 검색 (예시: '부산연산점' -> '연산')", key="branch_search")
    
    # ✅ 검색 결과 필터링
    if search_term:
        # 검색어가 있는 경우, 필터링된 결과를 DataFrame으로 유지
        filtered_branches = df[df["지점명"].str.contains(search_term, case=False, na=False)]
    else:
        # 검색어가 없는 경우, 빈 DataFrame 반환
        filtered_branches = pd.DataFrame(columns=df.columns)
    
    # ✅ 검색 결과가 없는 경우 처리
    if search_term and filtered_branches.empty:
        st.warning("⚠️ 일치하는 지점이 없습니다.")
        return
    
    # ✅ 지점 선택 드롭다운
    if not filtered_branches.empty:
        selected_branch = st.selectbox("지점 선택", filtered_branches["지점명"].unique())
    else:
        selected_branch = None
    
    # ✅ 선택된 지점 정보 표시
    if selected_branch:
        branch_data = df[df["지점명"] == selected_branch].iloc[0]
        locker_number = str(branch_data["사물함ID"]).strip()
        locker_password = str(branch_data["사물함PWD"]).strip()
        special_notes = branch_data.get("특이사항", "")  # 특이사항 컬럼 값 가져오기
        
        # ✅ 특이사항 팝업 (항상 표시)
        if special_notes and pd.notna(special_notes) and special_notes != "":
            with st.expander("🚨 특이사항 알림", expanded=True):
                st.write(special_notes)
        
        # ✅ 마스터키 안내 불가 팝업
        if locker_number == "***" and locker_password == "***":
            st.warning("🚨 해당 지점은 사물함 마스터키 안내가 불가합니다. 지점채널로 안내 부탁드립니다.")
            return
        elif locker_number == "***" or locker_password == "***":
            st.warning("🚨 특이사항: 사물함 정보가 누락되었습니다. 지점채널로 문의해주세요.")
            return
        
        # ✅ 현재 시간 (KST)
        kst = pytz.timezone('Asia/Seoul')
        current_time_kst = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
        
        # ✅ 안내문 생성
        info_text = (
            f"구매 확인이 완료되어 마스터키 발급이 완료되었습니다.\n"
            f"아래의 사물함에서 마스터키를 찾아 본인 사물함을 개방하시면 됩니다.\n\n"
            f"발급일시 : {current_time_kst}\n"
            f"지점명 : {selected_branch}\n"
            f"(1) 사물함 번호 : {locker_number}\n"
            f"(2) 비밀번호 : {locker_password}\n\n"
            "사물함 안에 마스터키가 들어 있습니다.\n"
            "비밀번호를 눌러 사물함을 열어주세요.\n\n"
            "🔑 마스터키 사용법:\n"
            "마스터키를 사물함의 키패드 중간에 보이는 '동그란 홈 부분'에 대면 문이 열립니다.\n\n"
            "🔐 사물함 비밀번호 설정 방법:\n"
            "문을 닫고, 원하는 4자리 비밀번호를 입력하세요.\n"
            "설정한 비밀번호를 다시 입력하면 문이 열립니다."
        )
        
        # ✅ 안내문 출력
        st.text_area("📌 마스터키 안내", info_text, height=400)

def convert_currency(currency_str):
    """통화 형식 문자열을 숫자로 변환 (예: '10,000원' → 10000)"""
    if not currency_str:
        return 0
    # 숫자와 쉼표만 추출
    cleaned = ''.join(filter(str.isdigit, currency_str))
    return int(cleaned) if cleaned else 0

def refund_calculator_page():
    st.title("💰 이용권 환불 계산")
    
    # Google Sheets에서 데이터 가져오기
    df = get_real_time_data()
    
    # 지점명 목록
    branch_list = df["지점명"].dropna().unique().tolist()

    # 지점명 검색 기능 (자동완성)
    search_term = st.text_input("🔍 지점명 입력 후 엔터 (예시: '부산연산점' -> '연산')", key="branch_search_refund")
    
    # 검색어 기반 지점명 필터링
    filtered_branches = []
    if search_term:
        filtered_branches = [branch for branch in branch_list if search_term.lower() in branch.lower()]
    
    # 지점명 선택 (드롭다운)
    selected_branch = None
    if filtered_branches:
        selected_branch = st.selectbox("검색된 지점 선택", filtered_branches, key="branch_select_refund")
    else:
        st.warning("⚠️ 일치하는 지점이 없습니다.")

    # 선택된 지점의 추가 정보 조회
    if selected_branch:
        branch_data = df[df["지점명"] == selected_branch].iloc[0]
        
        # 환불 정책 팝업
        with st.expander("📌 해당 지점 환불 정책", expanded=True):
            cols = st.columns(3)
            cols[0].metric("환불기간", branch_data.get("환불기간", "미입력"))
            cols[1].metric("환불응대금지", branch_data.get("환불응대금지", "미입력"))
            cols[2].metric("스터디룸 여부", branch_data.get("스터디룸 여부", "미입력"))

    # 기본 정보 입력 (지점명은 선택된 값으로 고정)
    branch = selected_branch if selected_branch else st.text_input("지점명 (수동입력)")
    phone = st.text_input("전화번호")
    ticket_type = st.radio("이용권 종류", ["기간권", "시간권", "노블레스석"])

    # ✅ formatted_ticket_type 변수 정의
    formatted_ticket_type = ticket_type  # 기본값으로 ticket_type을 사용

    # 환불 규정 자동 선택
    if selected_branch:
        branch_data = df[df["지점명"] == selected_branch].iloc[0]
    
        # 통화 형식 변환 적용
        time_price_str = branch_data.get("시간권금액", "0")
        period_price_str = branch_data.get("기간권금액", "0")
    
        # 통화 형식 변환 함수 호출
        time_price = convert_currency(time_price_str)
        period_price = convert_currency(period_price_str)
    
        # 시간권/기간권 금액이 유효한지 확인
        has_time_period_pricing = (time_price > 0) or (period_price > 0)
    
        if has_time_period_pricing:
            policy = "일반"
            st.info(f"📌 일반 환불 규정 적용 (시간권: {int(time_price):,}원, 기간권: {int(period_price):,}원)")
        else:
            policy = "% 규정"
            st.info("📌 % 환불 규정 적용")
    else:
        policy = st.radio("환불 규정", ["일반", "% 규정"])

    # 결제 및 환불 정보 입력
    ticket_price = st.number_input("결제 금액 (원)", min_value=0)
    purchase_date = st.date_input("결제일", value=datetime.now(pytz.timezone('Asia/Seoul')).date())
    refund_date = st.date_input("환불 요청일", value=datetime.now(pytz.timezone('Asia/Seoul')).date())
    
    # 위약금 선택 (0%, 10%, 20%)
    penalty_rate = st.selectbox("위약금 선택", ["0%", "10%", "20%"], index=0)
    
    # 이용권 종류에 따른 추가 입력 필드
    if ticket_type in ["기간권", "노블레스석"]:
        days_given = st.number_input("전체 부여 기간 [일] (기간권/노블레스석)", min_value=1)
    else:
        days_given = None
    
    if ticket_type == "시간권":
        weeks_given = st.number_input("유효 기간 [주] (시간권)", min_value=1)
        hours_used = st.number_input("사용 시간 (시간권)", min_value=0)
        total_hours = st.number_input("전체 부여 시간 (시간권)", min_value=1)
    else:
        weeks_given = None
        hours_used = None
        total_hours = None
    
    if ticket_type == "노블레스석":
        noble_rate = st.number_input("노블레스석 1일 요금 (원)", min_value=0)
    else:
        noble_rate = None
    
    # ▼▼▼ 유효기간 계산 수정 (결제일 포함) ▼▼▼
    if ticket_type == "시간권":
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(weeks=weeks_given)).strftime('%Y-%m-%d')}"
    else:
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(days=days_given - 1)).strftime('%Y-%m-%d')}" if days_given else "정보 없음"
    # ▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲▲

    # ▼▼▼ 환불 계산 로직 수정 ▼▼▼
    if st.button("환불 금액 계산"):
        # used_days 초기화 (모든 조건에서 사용 가능하도록)
        used_days = (refund_date - purchase_date).days + 1  # 결제일 포함

        # daily_rate, hourly_rate, noble_rate 설정
        daily_rate = period_price if ticket_type == "기간권" else 11000  # 시트의 기간권 금액 사용
        hourly_rate = time_price if ticket_type == "시간권" else 2000  # 시트의 시간권 금액 사용
        noble_rate = noble_rate if ticket_type == "노블레스석" else 0  # 노블레스석 1일 요금

        used_amount = 0
        refund_amount = 0  # refund_amount 초기화 추가

        # 결제일자 30일 초과 시 팝업 알림
        if (refund_date - purchase_date).days > 30:
            st.warning("결제한지 30일이 지났으므로 위약금이 발생하거나, 환불이 불가할 수 있습니다.")

        # 환불 규정에 따른 계산
        if policy == "% 규정":
            percent_used = (used_days / days_given) * 100 if ticket_type in ["기간권", "노블레스석"] else (hours_used / total_hours) * 100
        
            if percent_used < 25:
                refund_amount = ticket_price * 0.5
            elif percent_used < 50:
                refund_amount = ticket_price * 0.25
            else:
                refund_amount = 0
        
            # deduction_amount는 ticket_price - refund_amount로 계산
            deduction_amount = ticket_price - refund_amount
        
            # 사용량 정보 포맷 변경
            usage_info = (
                f"{percent_used:.1f}% 사용 ({used_days}일 사용)" 
                if ticket_type in ["기간권", "노블레스석"] 
                else f"{percent_used:.1f}% 사용 ({hours_used}시간 사용)"
            )
        
            # deduction_detail 설정
            if percent_used < 25:
                deduction_detail = f"0~24% 환불 구간 : 결제금액의 50% 환불 ({int(refund_amount):,}원)"
            elif percent_used < 50:
                deduction_detail = f"25~50% 환불 구간 : 결제금액의 25% 환불 ({int(refund_amount):,}원)"
            else:
                deduction_detail = f"50% 이상 사용 구간 : 환불 불가 ({int(deduction_amount):,}원)"
        else:
            # 일반 환불 규정
            if ticket_type == "기간권":
                used_amount = used_days * daily_rate
                usage_info = f"{used_days}일 사용"
                deduction_detail = f"{used_days}일 × {int(daily_rate):,}원"
            elif ticket_type == "노블레스석":
                used_amount = used_days * noble_rate
                usage_info = f"{used_days}일 사용"
                deduction_detail = f"{used_days}일 × {int(noble_rate):,}원 (노블레스석 1일 요금)"
            elif ticket_type == "시간권":
                used_amount = hours_used * hourly_rate
                usage_info = f"{hours_used}시간 사용"
                deduction_detail = f"{hours_used}시간 × {int(hourly_rate):,}원"
            else:
                used_amount = 0  # 기본값
                usage_info = "정보 없음"
                deduction_detail = "정보 없음"

            refund_amount = max(ticket_price - used_amount, 0)
            deduction_amount = used_amount  # 일반 환불 규정에서는 used_amount가 deduction_amount

        # 위약금 계산 (결제금액 기준)
        penalty_rate_value = int(penalty_rate.strip("%")) / 100  # 위약금 비율 (10% → 0.1)
        penalty_amount = ticket_price * penalty_rate_value  # 위약금 금액 (결제금액 기준)
        final_refund_amount = max(refund_amount - penalty_amount, 0)  # 최종 환불 금액 (음수 방지)
    
        # 한국 시간대 (KST)로 현재 시간 설정
        kst = pytz.timezone('Asia/Seoul')
        current_time_kst = datetime.now(kst).strftime('%Y-%m-%d %H:%M')
    
        # 환불 내역서 구성
        refund_detail = f"""
        [멘토즈 스터디카페 환불 내역서]
        =============================================
        ■ 지   점 : {branch}
        ■ 연락처 : {phone}
        ■ 발급일 : {current_time_kst}
        ---------------------------------------------
        [구 매 정 보]
        - 이용권 종류 : {formatted_ticket_type}
        - 결 제 일 자 : {purchase_date.strftime('%Y-%m-%d')}
        - 결제 금액 : {ticket_price:,}원
        - 유효 기간 : {valid_period}
        ---------------------------------------------
        [환 불 내역]
        ▣ 사용량 : {usage_info}
        ▣ 공제 금액 : {int(deduction_amount):,}원 ({deduction_detail})
        ▣ 위약금 : {int(penalty_amount):,}원 ({penalty_rate} 위약금)
        ▣ 환불 가능액 : {int(final_refund_amount):,}원
        ▶ 회원 정보 : {phone} (고객 전화번호 기준)
        =============================================
        ※ 유의사항
        - 본 내역서는 발급일 기준으로 유효합니다.
        - 결제일자로 부터 30일이 지난 결제건은 위약금이 추가로 발생할 수 있습니다.
        - 환불 처리에는 최대 3~5영업일이 소요될 수 있습니다.
        """
        
        # 환불 내역서 출력
        st.text_area("📄 환불 내역서 (Ctrl+C로 복사 가능)", refund_detail.strip(), height=400)

        # 계산 결과를 세션 상태에 저장
        st.session_state['refund_data'] = {
            'branch': branch,
            'phone': phone,
            'formatted_ticket_type': formatted_ticket_type,
            'purchase_date': purchase_date,
            'valid_period': valid_period,
            'ticket_price': ticket_price,
            'usage_info': usage_info,
            'used_amount': used_amount,
            'deduction_detail': deduction_detail,
            'penalty_rate': penalty_rate,
            'penalty_amount': penalty_amount,
            'final_refund_amount': final_refund_amount
        }

    # 계산 완료 후 계좌 정보 입력 폼 표시
    if 'refund_data' in st.session_state:
        st.markdown("---")
        st.subheader("✅ 환불 계좌 정보 입력")
        
        # 계좌 정보 입력 폼
        with st.form(key="account_form"):
            col1, col2 = st.columns(2)
            with col1:
                account_holder = st.text_input("예금주")
                bank_name = st.text_input("은행명")
            with col2:
                account_number = st.text_input("계좌번호")
            
            # 계좌 정보 확인 버튼
            if st.form_submit_button("확인"):
                st.session_state["account_info"] = {
                    'account_holder': account_holder,
                    'bank_name': bank_name,
                    'account_number': account_number
                }
                st.success("계좌 정보가 저장되었습니다.")
                st.rerun()  # 즉시 페이지 리로드

    # 계좌 정보가 입력된 경우 다운로드 버튼 표시
    if "account_info" in st.session_state:
        refund_data = st.session_state['refund_data']
        account_info = st.session_state['account_info']
        
        html_content = generate_refund_html(
            refund_data['branch'], refund_data['phone'], 
            refund_data['formatted_ticket_type'], refund_data['purchase_date'], 
            refund_data['valid_period'], refund_data['ticket_price'], 
            refund_data['usage_info'], refund_data['used_amount'], 
            refund_data['deduction_detail'], refund_data['penalty_rate'], 
            refund_data['penalty_amount'], refund_data['final_refund_amount'],
            account_info['account_holder'], account_info['bank_name'], 
            account_info['account_number']
        )
        
        st.download_button(
            label="📥 환불 영수증 다운로드 (HTML)",
            data=html_content,
            file_name="refund_receipt.html",
            mime="text/html"
        )
        
# ✅ HTML 템플릿 (기존과 동일)
def generate_refund_html(branch, phone, formatted_ticket_type, purchase_date, valid_period,
                        ticket_price, usage_info, used_amount, deduction_detail, penalty_rate,
                        penalty_amount, final_refund_amount, account_holder="", bank_name="", account_number=""):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @import url('https://cdn.jsdelivr.net/gh/orioncactus/Pretendard/dist/web/static/pretendard.css');
            body {{
                font-family: 'Pretendard', sans-serif;
                max-width: 400px; /* 좁은 너비 */
                margin: 20px auto;
                padding: 20px;
                background-color: #f8f9fa;
            }}
            .receipt {{
                background-color: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            .header {{
                text-align: center;
                border-bottom: 2px dashed #ddd;
                padding-bottom: 15px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 22px;
                font-weight: 700;
                color: #2c3e50;
                margin-bottom: 5px;
            }}
            .section {{
                margin: 15px 0;
            }}
            .section-title {{
                font-size: 16px;
                font-weight: 600;
                color: #34495e;
                margin-bottom: 10px;
            }}
            .info-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            .info-table td {{
                padding: 8px;
                border-bottom: 1px solid #eee;
            }}
            .highlight {{
                color: #e74c3c;
                font-weight: 700;
            }}
            .account-info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="receipt">
            <div class="header">
                <div class="title">멘토즈 스터디카페</div>
                <div style="font-size: 14px; color: #7f8c8d;">환불 요금 안내문</div>
            </div>

            <!-- 기본 정보 -->
            <div class="section">
                <div class="section-title">기본 정보</div>
                <table class="info-table">
                    <tr><td>지점명</td><td>{branch}</td></tr>
                    <tr><td>연락처</td><td>{phone}</td></tr>
                    <tr><td>이용권</td><td>{formatted_ticket_type}</td></tr>
                    <tr><td>유효기간</td><td>{valid_period}</td></tr>
                    <tr><td>환불요청일</td><td>{purchase_date.strftime('%Y-%m-%d')}</td></tr>
                </table>
            </div>

            <!-- 결제 정보 -->
            <div class="section">
                <div class="section-title">결제 정보</div>
                <table class="info-table">
                    <tr><td>결제 금액</td><td>{ticket_price:,}원</td></tr>
                    <tr><td>사용량</td><td>{usage_info}</td></tr>
                    <tr><td>공제 금액</td><td class="highlight">-{int(used_amount):,}원</td></tr>
                    <tr><td>공제 내역</td><td>{deduction_detail}</td></tr>
                    <tr><td>위약금 ({penalty_rate})</td><td class="highlight">-{int(penalty_amount):,}원</td></tr>
                    <tr><td>환불 가능액</td><td class="highlight">{int(final_refund_amount):,}원</td></tr>
                </table>
            </div>

            <!-- 환불 계좌 정보 -->
            <div class="account-info">
                <div class="section-title">환불 계좌 정보</div>
                <table class="info-table">
                    <tr><td>예금주</td><td>{account_holder}</td></tr>
                    <tr><td>은행명</td><td>{bank_name}</td></tr>
                    <tr><td>계좌번호</td><td>{account_number}</td></tr>
                </table>

                <div class="section" style="margin-top:30px;">
                    <div class="section-title">💳 입금 하실 금액</div>
                    <div style="font-size:24px; color:#2ecc71; font-weight:700; text-align:center;">
                        {int(used_amount):,}원
                </div>
            </div>

            <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                발급일: {datetime.now(pytz.timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M')}
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def restore_checkout_page():
    st.title("🛠️ 퇴실 미처리 복구")
    
    # ✅ 날짜 선택 (캘린더)
    checkout_date = st.date_input("퇴실 일자 선택", value=datetime.now(pytz.timezone('Asia/Seoul')).date())

    # ✅ 시간 입력 (텍스트 입력, HH:MM 형식)
    checkout_time_str = st.text_input("퇴실 시간 입력 (HH:MM 형식, 예: 15:30)", value="00:00")

    # ✅ 현재 시간 (기본값: 현재 시간)
    current_time = st.checkbox("현재 시간으로 설정", value=True)
    if current_time:
        now = datetime.now(pytz.timezone('Asia/Seoul'))
    else:
        now_date = st.date_input("현재 날짜 입력", value=datetime.now(pytz.timezone('Asia/Seoul')).date())
        now_time_str = st.text_input("현재 시간 입력 (HH:MM 형식, 예: 10:45)", value="00:00")
        try:
            now_time = datetime.strptime(now_time_str, "%H:%M").time()
            now = datetime.combine(now_date, now_time)
            now = pytz.timezone('Asia/Seoul').localize(now)
        except ValueError:
            st.error("❌ 올바른 시간 형식(HH:MM)을 입력하세요!")
            return

    # ✅ 폼 제출 버튼
    if st.button("미처리 시간 계산"):
        try:
            # ✅ 퇴실 시간 조합 (HH:MM 형식 파싱)
            checkout_time = datetime.strptime(checkout_time_str, "%H:%M").time()
            checkout_datetime = datetime.combine(checkout_date, checkout_time)
            checkout_datetime = pytz.timezone('Asia/Seoul').localize(checkout_datetime)

            # ✅ 퇴실 시간이 미래인지 확인
            if checkout_datetime > now:
                st.error("❌ 퇴실 시간이 미래일 수 없습니다!")
                return

            # ✅ 시간 차 계산
            lost_time = now - checkout_datetime
            lost_minutes = int(lost_time.total_seconds() // 60)
            lost_hours = lost_minutes // 60
            remaining_minutes = lost_minutes % 60
            extra_fee = (lost_minutes // 30) * 1000  # 30분당 1000원 초과 요금 계산

            # ✅ 결과 출력
            st.success(f"📅 미처리 기간: {checkout_datetime.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}")
            st.success(f"⏳ 미처리 시간: {lost_hours}시간 {remaining_minutes}분")
            st.success(f"💰 초과 요금: {extra_fee:,}원 (30분당 1,000원)")
        except ValueError:
            st.error("❌ 올바른 시간 형식(HH:MM)을 입력하세요!")
        except Exception as e:
            st.error(f"❌ 오류 발생: {str(e)}")

def main():
    if not check_password():
        st.stop()  # 인증되지 않으면 이후 코드 실행 안됨

    # ✅ 세션 상태 초기화
    if "page" not in st.session_state:
        st.session_state.page = "home"

    st.markdown(
        """
        <style>
        /* 지도 스타일 개선 */
        .folium-map {
            width: 100% !important;
            height: 540px !important;
            border-radius: 12px !important;
            margin: 15px 0 !important;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1) !important;
            border: 1px solid #e0e0e0 !important;
        }
        
        /* 확대/축소 버튼 스타일 */
        .leaflet-control-zoom {
            margin-right: 15px !important;
            margin-top: 70px !important;
            border: none !important;
            background: none !important;
        }
        .leaflet-control-zoom a {
            background-color: #fff !important;
            border-radius: 4px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
            color: #333 !important;
            width: 32px !important;
            height: 32px !important;
            line-height: 32px !important;
            margin-bottom: 4px !important;
        }
        .stExpander {
            margin-bottom: 20px;
        }
        .stExpander > div {
            padding: 10px;
        }
        .stExpander > div > div {
            white-space: pre-line;
        }
        .folium-map {
            width: 100% !important;
            height: 300px !important;
        }
    
        /* 노트북/프린트, 주차여부 간격 조정 */
        .stExpander > div {
            padding: 15px !important;
            margin: 10px 0 !important;
        }
        
        /* 지도 컨테이너 중앙 정렬 */
        .folium-map {
            margin: 10px auto !important;
            border-radius: 12px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 전체 페이지 CSS (main() 함수 상단 추가)
    st.markdown(
        """
        <style>
        /* 전체 폰트 및 색상 통일 */
        * {
            font-family: 'Pretendard', sans-serif !important;
        }

        /* 헤더 디자인 */
        .stApp header {
            background:rgb(239, 229, 229) !important;
            padding: 15px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        /* 입력 필드 통일성 추가 */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            border-radius: 8px !important;
            padding: 10px !important;
        }

        /* 버튼 디자인 */
        .stButton button {
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: all 0.3s !important;
        }

        /* 표 디자인 */
        .dataframe {
            border-radius: 8px !important;
            overflow: hidden !important;
        }
        
        
         /* 경고 메시지 스타일 */
         .stAlert {
            background-color: #ffebee !important;
            border-radius: 8px !important;
             padding: 15px !important;
        }

        /* 특이사항 팝업 스타일 */
        .stExpander {
            background-color: #fff3e0 !important;
            border-radius: 8px !important;
            padding: 15px !important;
        }

        
        /* 사이드바 버튼 스타일 */
        .sidebar .stButton button {
            background-color: #34495e !important;  /* 기본 색상 */
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
        }
        .sidebar .stButton button:hover {
            background-color: #3d566e !important;  /* 호버 시 색상 */
        }
        .sidebar .stButton button:active {
            background-color: #2ecc71 !important;  /* 활성화 시 색상 */
        }

        .material-chip {
            background: #e0f2f1;
            border-radius: 16px;
            padding: 4px 12px;
            display: inline-flex;
            align-items: center;
            margin: 4px;
        }
        .metric-card {
            background: #f5f5f5;
            border-radius: 12px;
            padding: 16px;
            margin: 8px 0;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 사이드바 스타일 적용
    st.markdown(
        """
        <style>
         /* 전체 폰트 및 색상 통일 */
        * {
            font-family: 'Pretendard', sans-serif !important;
        }

        /* 헤더 디자인 */
        .stApp header {
            background:rgb(239, 229, 229) !important;
            padding: 15px !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        /* 입력 필드 통일성 추가 */
        .stTextInput input, .stNumberInput input, .stDateInput input {
            border-radius: 8px !important;
            padding: 10px !important;
        }

        /* 버튼 디자인 */
        .stButton button {
            border-radius: 8px !important;
            padding: 10px 20px !important;
            transition: all 0.3s !important;
        }

        /* 표 디자인 */
        .dataframe {
            border-radius: 8px !important;
            overflow: hidden !important;
        }

        /* 경고 메시지 스타일 */
        .stAlert {
            background-color: #ffebee !important;
            border-radius: 8px !important;
            padding: 15px !important;
        }

        /* 사이드바 버튼 스타일 */
        .sidebar .stButton button {
            background-color: #34495e !important;  /* 기본 색상 */
            color: white !important;
            border-radius: 8px;
            padding: 8px 16px;
        }
        .sidebar .stButton button:hover {
            background-color: #3d566e !important;  /* 호버 시 색상 */
        }
        .sidebar .stButton button:active {
            background-color: #2ecc71 !important;  /* 활성화 시 색상 */
        }

        /* 사이드바 내 특이사항 팝업 스타일 수정 */
        .sidebar .stExpander {
            background-color: #fff3e0 !important;
            border-radius: 8px !important;
            padding: 15px !important;
        }

        /* 일반 팝업(Expander) 스타일 */
        .stExpander {
            background-color: #ffffff !important;
            border-radius: 8px !important;
            padding: 15px !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    
    )

     # 사이드바 제목에 이미지 추가
    st.sidebar.markdown(
        """
        <h2 style="text-align: center;">
            <img src="https://yesexpo.co.kr/wp-content/uploads/2022/06/%EB%A9%98%ED%86%A0%EC%A6%88-%EB%B8%8C%EB%9E%9C%EB%93%9C%EB%A1%9C%EA%B3%A0.png" width="200" height="auto"/>
    
        </h2>
        """,
        unsafe_allow_html=True
    )

    # ✅ 메뉴 아이템 리스트
    menu_items = [
        {"icon": "🏠", "label": "대시보드", "key": "home"},
        {"icon": "🔑", "label": "마스터키 관리", "key": "master", "sub": [
            {"label": "마스터키 안내", "key": "locker"},
            {"label": "퇴실 복구", "key": "restore"},
            {"label": "지점 정보 확인", "key": "branch_info"},
        ]},
        {"icon": "💰", "label": "환불 관리", "key": "refund", "sub": [
            {"label": "환불 계산", "key": "refund_calc"},
        ]},
        {"icon": "📊", "label": "데이터 관리", "key": "data", "sub": [
            {"label": "전체 지점 리스트", "key": "spreadsheet"},
        ]},
    ]

    # 메뉴 버튼 클릭 이벤트 처리
    for item in menu_items:
        if "sub" in item:  # 서브 메뉴가 있는 경우
            with st.sidebar.expander(f"{item['icon']} {item['label']}", expanded=True):  # 기본적으로 열려있도록 설정
                for sub_item in item["sub"]:
                    if st.button(
                        f"↳ {sub_item['label']}",
                        key=f"menu_{sub_item['key']}",  # key는 sub_item의 key로 지정
                        use_container_width=True,
                    ):
                        st.session_state.page = sub_item["key"]
        else:  # 일반 메뉴
            if st.sidebar.button(
                f"{item['icon']} {item['label']}",
                key=f"menu_{item['key']}",  # key는 item의 key로 지정
                use_container_width=True,
            ):
                st.session_state.page = item["key"]

    # ✅ 페이지 렌더링 함수
    def render_page():
        if st.session_state.page == "home":
            home_page()
        elif st.session_state.page == "locker":
            locker_masterkey_page()
        elif st.session_state.page == "restore":
            restore_checkout_page()
        elif st.session_state.page == "refund_calc":
            refund_calculator_page()
        elif st.session_state.page == "spreadsheet":
            load_and_display_spreadsheet_data()
        elif st.session_state.page == "branch_info":
            branch_info_page()

    # ✅ 메뉴 렌더링 함수 호출
    render_page()

  
if __name__ == "__main__":
    main()