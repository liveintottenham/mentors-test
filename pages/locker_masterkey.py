import tkinter as tk
from tkinter import messagebox

class LockerMasterKeyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("사물함 마스터키 안내")

        # 입력 필드
        tk.Label(root, text="사물함 번호").grid(row=0, column=0, padx=10, pady=10)
        self.entry_locker = tk.Entry(root)
        self.entry_locker.grid(row=0, column=1, padx=10, pady=10)
        self.entry_locker.bind("<Return>", self.display_masterkey_info)  # ✅ 엔터 키로 확인

        tk.Label(root, text="비밀번호").grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = tk.Entry(root)
        self.entry_password.grid(row=1, column=1, padx=10, pady=10)
        self.entry_password.bind("<Return>", self.display_masterkey_info)  # ✅ 엔터 키로 확인

        # 확인 버튼
        tk.Button(root, text="확인[enter]", command=self.display_masterkey_info).grid(row=2, column=0, columnspan=2, pady=10)

    def display_masterkey_info(self, event=None):
        """사물함 마스터키 정보를 새 창에 표시"""
        locker_number = self.entry_locker.get().strip()
        locker_password = self.entry_password.get().strip()

        if not locker_number or not locker_password:
            messagebox.showerror("입력 오류", "사물함 번호와 비밀번호를 입력하세요.")
            return

        # 새 창 생성
        result_window = tk.Toplevel(self.root)
        result_window.title("마스터키 안내")
        result_window.geometry("550x450")  # ✅ 크기 조정

        # 안내 메시지
        info_text = (
            "✅ 구매 확인 완료되어,\n"
            "사물함 마스터키 안내드립니다💛\n\n"
            f"🔑 [ {locker_number} ]번 사물함에 가셔서\n"
            f"비밀번호 [ {locker_password} ]을(를) 눌러주시면,\n"
            "내부에 마스터키가 들어 있습니다.\n"
            "키는 사용 후에 제자리에 넣고 다시 [ {locker_password} ] 입력하여 잠금 부탁드립니다.\n\n"
            "✅ 마스터키 사용 방법\n"
            "마스터키를 잠겨있는 사물함의\n"
            "키패드 중간에 보이는 ‘동그란 홈 부분’에 대시면 문이 열립니다.\n\n"
            "✅ 사물함 비밀번호 설정 방법\n"
            "문을 닫고 원하는 비밀번호 4자리를 누르세요.\n"
            "‘설정했던 비밀번호 4자리’를 다시 누르면 문이 열립니다."
        )

        # ✅ 스크롤 가능하게 설정
        text_frame = tk.Frame(result_window)
        text_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('맑은 고딕', 10), height=15)
        text_widget.insert(tk.END, info_text)
        text_widget.config(state=tk.DISABLED)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll_bar = tk.Scrollbar(text_frame, command=text_widget.yview)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scroll_bar.set)

        # 버튼 프레임 생성
        btn_frame = tk.Frame(result_window)
        btn_frame.pack(pady=10)

        # 복사 버튼
        tk.Button(btn_frame, text="복사하기", command=lambda: self.copy_to_clipboard(info_text)).pack(side=tk.LEFT, padx=5)

        # 닫기 버튼
        tk.Button(btn_frame, text="닫기", command=result_window.destroy).pack(side=tk.LEFT, padx=5)

    def copy_to_clipboard(self, text):
        """내용을 클립보드에 복사"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        messagebox.showinfo("복사 완료", "사물함 마스터키 안내가 클립보드에 복사되었습니다!")

# ✅ 실행 코드
if __name__ == "__main__":
    root = tk.Tk()
    app = LockerMasterKeyApp(root)
    root.mainloop()
