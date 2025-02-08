import streamlit as st
from datetime import datetime, timedelta
import pytz, gspread, random, string, os, json
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# ✅ 페이지 설정
st.set_page_config(
    page_title="멘토즈 가맹관리부 시스템",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
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

# ✅ 비밀번호 확인 함수
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if st.session_state.authenticated:
        return True
    
    st.markdown("## 🔐 접근 제한")
    password = st.text_input("비밀번호를 입력하세요", type="password", key="login_password")
    if st.button("로그인"):
        if password == "1234":  # ✅ 비밀번호 설정
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 틀렸습니다!")
    
    return st.session_state.authenticated

# ✅ Google Sheets 인증 함수 (start)
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

# ✅ 실시간 데이터 조회
@st.cache_data(ttl=5, show_spinner=False)
def get_real_time_data():
    try:
        client = authenticate_google_sheets()
        spreadsheet = client.open("멘토즈 지점 정보")
        sheet = spreadsheet.worksheet("시트1")
        df = pd.DataFrame(sheet.get_all_records())
        
        # ✅ '마스터키 PWD' 열을 문자열로 강제 변환
        df["마스터키 PWD"] = df["마스터키 PWD"].astype(str)
        return df
    
    except Exception as e:
        st.error(f"📊 데이터 조회 실패: {str(e)}")
        return pd.DataFrame()

# ✅ 데이터 업데이트 함수
def update_sheet(new_data):
    try:
        client = authenticate_google_sheets()
        spreadsheet = client.open("멘토즈 지점 정보")
        sheet = spreadsheet.worksheet("시트1")

        # ✅ 헤더 포함 전체 데이터 업데이트
        sheet.clear()
        sheet.update(
            [new_data.columns.tolist()] + 
            new_data.astype(str).values.tolist()
        )
        st.cache_data.clear()
        
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

# ✅ Streamlit UI 시작
def load_and_display_spreadsheet_data():
    st.title("📊 스프레드시트 데이터 관리")

    # ✅ 실시간 데이터 가져오기
    df = get_real_time_data()

    # ✅ 지점명 검색 필드 추가
    branch_name = st.text_input("🔍 지점명 검색", key=f"branch_search_{st.session_state.random_id}")

    # ✅ 검색된 지점명에 맞춰 데이터 필터링
    filtered_df = df[df["지점명"].str.contains(branch_name, case=False, na=False)] if branch_name else df

    # ✅ Streamlit 데이터 표시 (읽기 전용)
    st.subheader("📊 현재 데이터")
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
            with st.expander("📝 새 지점 정보 추가", expanded=True):
                new_row = {}
                for col in df.columns:
                    # ✅ '마스터키 PWD'는 문자열로만 입력받기
                    if col == "마스터키 PWD":
                        new_row[col] = st.text_input(f"{col} 입력", key=f"new_{col}_{st.session_state.random_id}")
                    else:
                        # 다른 열의 데이터 타입에 맞게 처리
                        if df[col].dtype == "int64":
                            new_row[col] = st.number_input(f"{col} 입력", key=f"new_{col}_{st.session_state.random_id}")
                        elif df[col].dtype == "float64":
                            new_row[col] = st.number_input(f"{col} 입력", key=f"new_{col}_{st.session_state.random_id}", format="%.2f")
                        else:
                            new_row[col] = st.text_input(f"{col} 입력", key=f"new_{col}_{st.session_state.random_id}")
            
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
                        update_sheet(updated_df)
                        st.success("✅ 데이터가 성공적으로 추가되었습니다!")
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

def main():
    if not check_password():
        st.stop()  # 인증되지 않으면 이후 코드 실행 안됨

    # ✅ 세션 상태 초기화
    if "page" not in st.session_state:
        st.session_state.page = "home"

    # ✅ 사이드바 스타일 적용
    st.sidebar.markdown(
        """
        <style>
        /* 사이드바 전체 스타일 */
        .stSidebar {
            background-color: #2c3e50 !important;
            font-family: 'Roboto', sans-serif;
        }

        /* 타이틀 스타일 */
        .sidebar-title {
            font-size: 28px;
            font-weight: bold;
            text-align: center;
            color: #ffffff;
            margin-bottom: 30px;
            padding: 15px;
            background-color: #34495e;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* 메뉴 아이템 스타일 */
        .sidebar-item {
            display: flex;
            align-items: center;
            padding: 12px 20px;
            margin: 8px 0;
            font-size: 16px;
            color: #ffffff;
            background-color: #3498db;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        /* 메뉴 아이템 호버 효과 */
        .sidebar-item:hover {
            background-color: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }

        /* 활성화된 메뉴 */
        .sidebar-item.active {
            background-color: #2ecc71 !important;
            color: white !important;
        }

        /* 아이콘 스타일 */
        .sidebar-icon {
            margin-right: 10px;
            font-size: 20px;
        }

        /* 구분선 스타일 */
        .sidebar-divider {
            border-top: 1px solid #34495e;
            margin: 20px 0;
        }

        /* 푸터 스타일 */
        .sidebar-footer {
            text-align: center;
            font-size: 12px;
            color: #bdc3c7;
            margin-top: 30px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # ✅ 사이드바 타이틀
    st.sidebar.markdown('<p class="sidebar-title">⭐❤️</p>', unsafe_allow_html=True)

    # ✅ 메뉴 아이템 리스트
    menu_items = [
        {"icon": "🏠", "label": "홈", "key": "home"},
        {"icon": "🔑", "label": "사물함 마스터키", "key": "locker"},
        {"icon": "🔄", "label": "퇴실 미처리 복구", "key": "restore"},
        {"icon": "💰", "label": "이용권 환불 계산", "key": "refund"},
        {"icon": "📊", "label": "멘토즈 지점명/특이사항", "key": "spreadsheet"},
    ]

    # ✅ 사이드바 메뉴 UI
    for item in menu_items:
        if st.sidebar.button(f"{item['icon']} {item['label']}", key=f"menu_{item['key']}", use_container_width=True):
            st.session_state.page = item['key']
            st.rerun()  # 페이지 업데이트

    # ✅ 선택한 페이지 실행
    if st.session_state.page == "home":
        home_page()
    elif st.session_state.page == "locker":
        locker_masterkey_page()
    elif st.session_state.page == "restore":
        restore_checkout_page()
    elif st.session_state.page == "refund":
        refund_calculator_page()
    elif st.session_state.page == "spreadsheet":
        load_and_display_spreadsheet_data()

# ✅ 홈 페이지
def home_page():
    st.markdown(
        """
        <style>
        .stApp { background-color: #f5f7fa; }
        .title-text { text-align: center; font-size: 40px; font-weight: bold; color: white; background-color: #2c3e50; padding: 15px; border-radius: 10px; }
        .sub-title { text-align: center; font-size: 20px; color: #ffffff; background-color: #34495e; padding: 10px; border-radius: 10px; }
        .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin: 10px 0; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # ✅ 공지사항 데이터
    notices = [
        {"날짜": "2025-02-08", "제목": "멘토즈 가맹관리부 시스템 업로드", "링크": "https://example.com"},
        {"날짜": "2025-02-01", "제목": "test 내용 ", "링크": "https://example.com"},
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
        st.subheader("📢 공지사항")
        for notice in notices:
            st.markdown(
                f"""
                <div class="card">
                    <h4>✅ {notice['날짜']}</h4>
                    <p><strong>{notice['제목']}</strong></p>
                    <a href="{notice['링크']}" target="_blank">🔗 바로가기</a>
                </div>
                """, unsafe_allow_html=True
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

# ✅ 사물함 마스터키 페이지
def locker_masterkey_page():
    st.title("🛠️ 사물함 마스터키 안내")
    st.subheader("사물함의 마스터키를 한눈에 볼 수 있어요.")
    locker_number = st.text_input("사물함 번호를 입력하세요", key="locker_number")
    locker_password = st.text_input("사물함 비밀번호 입력", type="password", key="locker_password")
    
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
    st.title("🛠️ 퇴실 미처리 복구")
    
    # 날짜와 시간 입력 필드
    checkout_date = st.text_input("퇴실 일자 (YYYYMMDD)")  # 예: 20250130
    checkout_time = st.text_input("퇴실 시간 (HHMM)")  # 예: 1530

    kst = pytz.timezone('Asia/Seoul')
    now = datetime.now(kst)  # 현재 시간을 한국 시간대로 가져오기

    with st.form(key="checkout_form"):
        # 폼 제출 버튼
        submit_button = st.form_submit_button("미처리 시간 계산")

    if submit_button:  # 엔터를 누르면 제출 버튼이 활성화됨
        if checkout_date and checkout_time:  # 값이 입력되었을 때만 실행
            try:
                # 2자리 연도를 4자리로 보정 (예: '250130' -> '20250130')
                if len(checkout_date) == 6:
                    checkout_date = "20" + checkout_date  # 2자리 연도를 4자리로 보정

                # 사용자가 입력한 퇴실 날짜와 시간 문자열을 datetime 객체로 변환
                checkout_datetime = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y%m%d %H%M")
                checkout_datetime = kst.localize(checkout_datetime)  # 입력된 날짜와 시간을 한국 시간대에 맞게 변환

                if checkout_datetime > now:
                    st.error("❌ 퇴실 시간이 미래일 수 없습니다!")
                    return

                # 시간 차 계산
                lost_time = now - checkout_datetime
                lost_minutes = int(lost_time.total_seconds() // 60)
                lost_hours = lost_minutes // 60
                remaining_minutes = lost_minutes % 60
                extra_fee = (lost_minutes // 30) * 1000  # 30분당 1000원 초과 요금 계산

                # 결과 출력
                st.success(f"📅 미처리 기간: {checkout_datetime.strftime('%Y-%m-%d %H:%M')} ~ {now.strftime('%Y-%m-%d %H:%M')}")
                st.success(f"⏳ 미처리 시간: {lost_hours}시간 {remaining_minutes}분")
                st.success(f"💰 초과 요금: {extra_fee:,}원 (30분당 1,000원)")
            except ValueError:
                st.error("❌ 올바른 날짜 및 시간 형식을 입력하세요!")
        else:
            st.error("❌ 퇴실 일자와 시간을 입력하세요!")



def refund_calculator_page():
    st.title("💰 이용권 환불 계산")
    
    # 기본 정보 입력
    branch = st.text_input("지점명")
    phone = st.text_input("전화번호")
    ticket_type = st.radio("이용권 종류", ["기간권", "시간권", "노블레스석"])
    policy = st.radio("환불 규정", ["일반", "% 규정"])
    
    # 결제 및 환불 정보 입력 (날짜는 기본값으로 오늘 날짜 설정)
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
    
    # 유효 기간 계산
    if ticket_type == "시간권":
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(weeks=weeks_given)).strftime('%Y-%m-%d')}"
    else:
        valid_period = f"{purchase_date.strftime('%Y-%m-%d')} ~ {(purchase_date + timedelta(days=days_given-1)).strftime('%Y-%m-%d')}" if days_given else "정보 없음"
    
    # 이용권 종류 표시 형식 수정
    formatted_ticket_type = f"{ticket_type} ({days_given}일)" if ticket_type != "시간권" else f"{ticket_type} ({total_hours}시간)"
    
    # 환불 금액 계산 (엔터 키로도 실행 가능)
    if st.button("환불 금액 계산"):  # 항상 계산 실행
        used_days = (refund_date - purchase_date).days + 1
        daily_rate = 11000
        hourly_rate = 2000
        used_amount = 0
        
        # 결제일자 30일 초과 시 팝업 알림
        if (refund_date - purchase_date).days > 30:
            st.warning("결제한지 30일이 지났으므로 위약금이 발생하거나, 환불이 불가할 수 있습니다.")
        
        # 환불 규정에 따른 계산
        if policy == "% 규정":
            percent_used = (used_days / days_given) * 100 if ticket_type in ["기간권", "노블레스석"] else (hours_used / total_hours) * 100
            
            if percent_used < 25:
                refund_amount = ticket_price * 0.5
                deduction_amount = ticket_price * 0.5
                deduction_detail = f"0~24% 환불 구간 : 결제금액의 50% 환불 ({deduction_amount:,.0f}원)"
            elif percent_used < 50:
                refund_amount = ticket_price * 0.25
                deduction_amount = ticket_price * 0.75
                deduction_detail = f"25~50% 환불 구간 : 결제금액의 25% 환불 ({deduction_amount:,.0f}원)"
            else:
                refund_amount = 0
                deduction_amount = ticket_price
                deduction_detail = f"50% 이상 사용 구간 : 환불 불가 ({deduction_amount:,.0f}원)"
            
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
        ▣ 공제 금액 : -{used_amount:,}원 ({deduction_detail})
        ▣ 위약금 : -{penalty_amount:,.0f}원 ({penalty_rate} 위약금)
        ▣ 환불 금액 : {int(final_refund_amount):,}원
        ▶ 회원 정보 : {phone} (고객 전화번호 기준)
        =============================================
        ※ 유의사항
        - 본 내역서는 발급일 기준으로 유효합니다.
        - 결제일자로 부터 30일이 지난 결제건은 위약금이 추가로 발생할 수 있습니다.
        - 환불 처리에는 최대 3~5영업일이 소요될 수 있습니다.
        """
        
        # 환불 내역서 출력
        st.text_area("📄 환불 내역서 (Ctrl+C로 복사 가능)", refund_detail.strip(), height=400)
        st.download_button("📥 환불 내역서 다운로드", refund_detail.strip(), file_name="refund_details.txt")
  
if __name__ == "__main__":
    main()