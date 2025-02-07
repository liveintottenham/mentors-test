import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime, timedelta

# 동적 UI 관리를 위한 클래스
class DynamicUI:
    def __init__(self, root):
        self.root = root
        self.ticket_fields = {
            "기간권": ["days_given"],
            "시간권": ["hours_used", "total_hours", "valid_weeks"],  # valid_weeks 추가
            "노블레스석": ["days_given"]
        }
        
    def show_fields(self, ticket_type):
        # 모든 필드 숨기기
        for field in self.ticket_fields.values():
            for f in field:
                label, entry = getattr(self.root, f"row_{f}")
                label.grid_remove()
                entry.grid_remove()
        
        # 선택한 이용권 필드 표시
        if ticket_type in self.ticket_fields:
            for f in self.ticket_fields[ticket_type]:
                label, entry = getattr(self.root, f"row_{f}")
                label.grid()
                entry.grid()

# 환불 계산기 클래스
class RefundCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("이용권 환불 계산 프로그램")
        self.ui = DynamicUI(self.root)
        self.root.geometry("400x600")  # 창 크기 조정 (가로x세로)
        
        self.daily_rate = 11000  # 기본 1일 요금
        self.setup_ui()

    def setup_ui(self):
        # 이용권 선택
        tk.Label(self.root, text="이용권 선택").grid(row=0, column=0, padx=10, pady=10)
        self.ticket_var = tk.StringVar(value="기간권")
        tk.Radiobutton(self.root, text="기간권", variable=self.ticket_var, value="기간권", 
                      command=lambda: self.ui.show_fields("기간권")).grid(row=0, column=1)
        tk.Radiobutton(self.root, text="시간권", variable=self.ticket_var, value="시간권",
                      command=lambda: self.ui.show_fields("시간권")).grid(row=0, column=2)
        tk.Radiobutton(self.root, text="노블레스석", variable=self.ticket_var, value="노블레스석",
                      command=lambda: self.ui.show_fields("노블레스석")).grid(row=0, column=3)

        # 환불 규정 선택
        tk.Label(self.root, text="환불 규정").grid(row=1, column=0, padx=10, pady=10)
        self.policy_var = tk.StringVar(value="일반")
        tk.Radiobutton(self.root, text="일반", variable=self.policy_var, value="일반").grid(row=1, column=1)
        tk.Radiobutton(self.root, text="% 규정", variable=self.policy_var, value="%").grid(row=1, column=2)

        # 공통 입력 필드
        self.create_common_fields()
        
        # 동적 필드 초기화
        self.init_dynamic_fields()
        self.ui.show_fields("기간권")

    def create_common_fields(self):
        # 공통 입력 필드 생성
        fields = [
            ("지점명", "branch", 2),
            ("전화번호", "phone", 3),
            ("결제일 (YYYYMMDD)", "purchase_date", 4),
            ("환불요청일 (YYYYMMDD)", "refund_date", 5),
            ("결제금액", "ticket_price", 6)
        ]
        
        for text, var_name, row in fields:
            tk.Label(self.root, text=text).grid(row=row, column=0, padx=10, pady=10)
            entry = tk.Entry(self.root)
            entry.grid(row=row, column=1, columnspan=3, padx=10, pady=10)
            setattr(self, f"entry_{var_name}", entry)

    def init_dynamic_fields(self):
        # 동적 필드 생성
        self.create_dynamic_field("부여일자", "days_given", 7, "기간권/노블레스석")
        self.create_dynamic_field("사용시간", "hours_used", 8, "시간권")
        self.create_dynamic_field("총 시간", "total_hours", 9, "시간권")
        self.create_dynamic_field("유효기간(주)", "valid_weeks", 10, "시간권")  # 시간권 유효기간(주) 추가

    def create_dynamic_field(self, text, var_name, row, ticket_type):
        label = tk.Label(self.root, text=text)
        entry = tk.Entry(self.root)
        setattr(self.root, f"row_{var_name}", (label, entry))
        setattr(self, f"entry_{var_name}", entry)  # 동적 필드를 self에 저장
        label.grid(row=row, column=0, padx=10, pady=10)
        entry.grid(row=row, column=1, columnspan=3, padx=10, pady=10)
        label.grid_remove()
        entry.grid_remove()

    def calculate(self):
        try:
            ticket_type = self.ticket_var.get()
            policy = self.policy_var.get()
            
            # 노블레스석 일반 규정 시 추가 입력
            if ticket_type == "노블레스석" and policy == "일반":
                self.daily_rate = simpledialog.askinteger("1일 요금 입력", "1일 사용 금액을 입력하세요:", parent=self.root)
                if not self.daily_rate:
                    return

            # 공통 데이터 수집
            data = self.collect_data()
            result = self.process_calculation(ticket_type, policy, data)
            self.show_result(result)

        except Exception as e:
            messagebox.showerror("오류", f"입력값 오류: {str(e)}")

    def collect_data(self):
        return {
            'branch': self.entry_branch.get(),
            'phone': self.entry_phone.get(),
            'purchase_date': datetime.strptime(self.entry_purchase_date.get(), "%Y%m%d"),
            'refund_date': datetime.strptime(self.entry_refund_date.get(), "%Y%m%d"),
            'ticket_price': int(self.entry_ticket_price.get()),
            'days_given': int(self.entry_days_given.get()) if self.ticket_var.get() in ["기간권", "노블레스석"] else 0,
            'hours_used': int(self.entry_hours_used.get()) if self.ticket_var.get() == "시간권" else 0,
            'total_hours': int(self.entry_total_hours.get()) if self.ticket_var.get() == "시간권" else 0,
            'valid_weeks': int(self.entry_valid_weeks.get()) if self.ticket_var.get() == "시간권" else 0  # 시간권 유효기간(주)
        }

    def process_calculation(self, ticket_type, policy, data):
        used_days = (data['refund_date'] - data['purchase_date']).days + 1
        
        if policy == "일반":
            return self.calculate_normal(ticket_type, data, used_days)
        else:
            return self.calculate_percent(ticket_type, data, used_days)

    def calculate_normal(self, ticket_type, data, used_days):
        if ticket_type == "기간권":
            used_amount = used_days * 11000
            policy_str = f"{used_days}일 × 11,000원"
        elif ticket_type == "시간권":
            used_amount = data['hours_used'] * 2000
            policy_str = f"{data['hours_used']}시간 × 2,000원"
        else:  # 노블레스석
            used_amount = used_days * self.daily_rate
            policy_str = f"{used_days}일 × {self.daily_rate:,}원"

        return {
            'policy': policy_str,
            'used': used_amount,
            'refund': data['ticket_price'] - used_amount,
            'usage_info': self.get_usage_info(ticket_type, data, used_days)
        }
    
    def _format_usage_info(self, usage_info):
        if "시간" in usage_info:
            return f"- 사용 시간 : {usage_info.replace('중', '')}"
        return f"- 사용 일수 : {usage_info.replace('중', '')}"
    
    def _format_refund_info(self, result):
        return f"""▣ 결제 금액 : {result['refund'] + result['used']:,}원
        ▣ 공제 금액 : {result['used']:,}원 ({result['policy']})
        ▣ 환불 금액 : {result['refund']:,}원
        ▶ 회원 정보 : {self.entry_phone.get()} (고객 전화번호 기준)"""

    def calculate_percent(self, ticket_type, data, used_days):
        if ticket_type in ["기간권", "노블레스석"]:
            total = data['days_given']
            used = used_days
        else:  # 시간권
            total = data['total_hours']
            used = data['hours_used']

        percent = int((used / total) * 100)  # 소수점 제거 후 정수로 변환
        policy_info = self.get_policy_by_percent(percent, data['ticket_price'])
    
        return {
            'policy': policy_info['desc'],
            'used': policy_info['amount'],
            'refund': data['ticket_price'] - policy_info['amount'],
            'usage_info': f"{total}중 {used} 사용 ({percent}%)"  # 소수점 없이 정수로 표시
    }

    def get_policy_by_percent(self, percent, price):
        if percent <= 25:
            return {'amount': price * 0.5, 'desc': "0~25% 사용 → 50% 환불"}
        elif percent <= 50:
            return {'amount': price * 0.75, 'desc': "26~50% 사용 → 25% 환불"}
        else:
            return {'amount': price, 'desc': "50% 초과 → 환불 불가"}

    def get_usage_info(self, ticket_type, data, used_days):
        if ticket_type == "시간권":
            return f"총 {data['total_hours']}시간 중 {data['hours_used']}시간 사용"
        return f"총 {data['days_given']}일 중 {used_days}일 사용"

    def _get_valid_period(self):
        try:
            purchase_date = datetime.strptime(self.entry_purchase_date.get(), "%Y%m%d")
            if self.ticket_var.get() == "시간권":
                # 시간권: 유효기간(주)를 입력받아 계산
                valid_weeks = int(self.entry_valid_weeks.get())
                end_date = purchase_date + timedelta(weeks=valid_weeks)
            else:
                # 기간권/노블레스석: 부여일자를 입력받아 계산
                days_given = int(self.entry_days_given.get())
                end_date = purchase_date + timedelta(days=days_given)
            return f"{purchase_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
        except:
            return "정보 없음"

    def show_result(self, result):
        result_window = tk.Toplevel(self.root)
        result_window.title("환불 계산 결과")

        # 결과 텍스트 구성
        text = f"""
        {result['usage_info']}
        [결제금액] {result['refund'] + result['used']:,}원
        [사용금액] {result['used']:,}원 ({result['policy']})
        --------------------------
        [환불금액] {result['refund']:,}원
        """

        if (datetime.now() - datetime.strptime(self.entry_purchase_date.get(), "%Y%m%d")).days > 30:
            text += "\n※ 결제 후 30일이 초과되어 환불이 제한될 수 있습니다."

        tk.Label(result_window, text=text.strip()).pack(padx=20, pady=20)
        tk.Button(result_window, text="상세 보기", 
                 command=lambda: self.show_detail(result)).pack(pady=10)
        tk.Button(result_window, text="닫기", command=result_window.destroy).pack(pady=10)

    def show_detail(self, result):
        detail_window = tk.Toplevel(self.root)
        detail_window.title("상세 환불 내역")
        detail_window.geometry("500x600")

        # 전문적인 양식 구성
        detail_text = f"""
        [멘토즈 스터디카페 환불 내역서]
        {'='*45}
        ■ 지   점 : {self.entry_branch.get()}
        ■ 연락처 : {self.entry_phone.get()}
        ■ 발급일 : {datetime.now().strftime('%Y-%m-%d %H:%M')}
        {'-'*45}
        [구 매 정 보]
        - 이용권 종류 : {self.ticket_var.get()}
        - 결 제 일 자 : {self.entry_purchase_date.get()}
        - 결제 금액 : {result['refund'] + result['used']:,}원
        - 유효 기간 : {self._get_valid_period()}
        {'-'*45}
        [사 용 내 역]
        {self._format_usage_info(result['usage_info'])}
        {'-'*45}
        [환 불 내 역]
        {self._format_refund_info(result)}
        {'='*45}
        ※ 유의사항
        - 본 내역서는 발급일 기준으로 유효합니다.
        - 환불 처리에는 최대 3~5영업일이 소요될 수 있습니다.
        """

        text_widget = tk.Text(detail_window, wrap=tk.WORD, font=('맑은 고딕', 10))
        text_widget.insert(tk.END, detail_text.strip())
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(detail_window)
        btn_frame.pack(pady=10)
    
        tk.Button(btn_frame, text="양식 복사", 
                command=lambda: self.copy_to_clipboard(detail_text)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="닫기", 
                command=detail_window.destroy).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("복사 완료", "클립보드에 텍스트가 복사되었습니다.")

    def run(self):
        # 계산 버튼
        tk.Button(self.root, text="계산 시작", command=self.calculate).grid(row=11, column=0, columnspan=4, pady=20)
        self.root.mainloop()

if __name__ == "__main__":
    app = RefundCalculator()
    app.run()
