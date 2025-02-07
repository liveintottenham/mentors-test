import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

class RestoreCheckoutApp:
    def __init__(self, root):
        self.root = root
        self.root.title("퇴실 미처리 복구")

        # 날짜 입력 (YYYYMMDD)
        tk.Label(root, text="퇴실 일자 (YYYYMMDD)").grid(row=0, column=0, padx=10, pady=10)
        self.entry_date = tk.Entry(root)
        self.entry_date.grid(row=0, column=1, padx=10, pady=10)
        self.entry_date.bind("<Return>", self.calculate_unchecked_out)  # ✅ 엔터 키로 계산 가능

        # 시간 입력 (HHMM)
        tk.Label(root, text="퇴실 시간 (HHMM)").grid(row=1, column=0, padx=10, pady=10)
        self.entry_time = tk.Entry(root)
        self.entry_time.grid(row=1, column=1, padx=10, pady=10)
        self.entry_time.bind("<Return>", self.calculate_unchecked_out)  # ✅ 엔터 키로 계산 가능

        # 계산 버튼
        tk.Button(root, text="미처리 시간 계산", command=self.calculate_unchecked_out).grid(row=2, column=0, columnspan=2, pady=10)

        # 결과 표시 (✅ 왼쪽 정렬 적용)
        self.result_label = tk.Label(root, text="", font=("맑은 고딕", 12, "bold"), justify="left", anchor="w")
        self.result_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        # 복사 버튼
        self.copy_button = tk.Button(root, text="결과 복사", command=self.copy_to_clipboard, state=tk.DISABLED)
        self.copy_button.grid(row=4, column=0, columnspan=2, pady=10)

    def calculate_unchecked_out(self, event=None):
        """입력된 퇴실 정보를 기반으로 미처리 시간을 분 단위까지 계산하고 초과 요금 표시"""
        try:
            checkout_date = self.entry_date.get().strip()  # YYYYMMDD 형식
            checkout_time = self.entry_time.get().strip()  # HHMM 형식

            # 입력값 검증
            if len(checkout_date) != 8 or not checkout_date.isdigit():
                raise ValueError("올바른 날짜 형식(YYYYMMDD)을 입력하세요.")

            if len(checkout_time) != 4 or not checkout_time.isdigit():
                raise ValueError("올바른 시간 형식(HHMM)을 입력하세요.")

            # 날짜 및 시간 변환
            checkout_datetime = datetime.strptime(f"{checkout_date} {checkout_time}", "%Y%m%d %H%M")

            # 현재 시간과 비교하여 미처리 시간 계산
            now = datetime.now()
            if checkout_datetime > now:
                messagebox.showerror("오류", "퇴실 시간이 미래일 수 없습니다.")
                return

            lost_time = now - checkout_datetime  # 차이 계산
            lost_minutes = int(lost_time.total_seconds() // 60)  # 분 단위 변환
            lost_hours = lost_minutes // 60
            remaining_minutes = lost_minutes % 60  # 초과된 분 계산

            # 초과 요금 계산 (30분당 1,000원)
            extra_fee_units = lost_minutes // 30  # 30분 단위로 나누기
            extra_fee = extra_fee_units * 1000  # 30분당 1,000원 적용

            # ✅ 미처리된 기간 (퇴실 시간 ~ 현재 시간)
            period_text = f"📅 미처리 기간: {checkout_datetime.strftime('%Y%m%d %H:%M')} ~ {now.strftime('%Y%m%d %H:%M')}"

            # ✅ 초과 요금 설명 추가 (30분당 1,000원 고정 표시)
            result_text = (
                f"{period_text}\n"
                f"⏳ 미처리 시간: {lost_hours}시간 {remaining_minutes}분\n"
                f"💰 초과 요금: {extra_fee:,}원 (30분당 1,000원)"
            )

            self.result_label.config(text=result_text, justify="left", anchor="w")  # ✅ 왼쪽 정렬 적용
            self.copy_button.config(state=tk.NORMAL)  # 복사 버튼 활성화

            # 결과 저장 (복사용)
            self.result_data = result_text

        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))

    def copy_to_clipboard(self):
        """결과를 클립보드에 복사"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.result_data)
        self.root.update()
        messagebox.showinfo("복사 완료", "결과가 클립보드에 복사되었습니다!")

# ✅ 퇴실 복구 프로그램 실행 코드
if __name__ == "__main__":
    root = tk.Tk()
    app = RestoreCheckoutApp(root)
    root.mainloop()
