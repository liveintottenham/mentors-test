import tkinter as tk
import subprocess
import os
import sys # 여러 프로그램 실행

if getattr(sys, 'frozen', False):
    script_dir = sys._MEIPASS  # PyInstaller 실행 시 임시 폴더
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # 일반 실행 시

# 실행할 하위 파일 경로 설정
locker_script = os.path.join(script_dir, "locker_masterkey.py")
refund_script = os.path.join(script_dir, "refund112.py")
restore_script = os.path.join(script_dir, "restore_checkout.py")

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("메인 화면")

        tk.Label(root, text="환불 계산 프로그램", font=("맑은 고딕", 14, "bold")).pack(pady=20)

        # 버튼 추가
        tk.Button(root, text="[a] 환불 계산기 실행", command=self.start_refund_calculator, width=25, height=2).pack(pady=10)
        tk.Button(root, text="[b] 퇴실 미처리 복구", command=self.start_restore_checkout, width=25, height=2).pack(pady=10)
        tk.Button(root, text="[c] 사물함 마스터키 안내", command=self.start_locker_masterkey, width=25, height=2).pack(pady=10)

    def start_refund_calculator(self):
        """[a] 버튼: refund112.py 실행"""
        script_path = os.path.abspath("refund112.py")
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["python", script_path], startupinfo=startupinfo)
        except FileNotFoundError:
            tk.messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{script_path}")

    def start_restore_checkout(self):
        """[b] 버튼: restore_checkout.py 실행"""
        script_path = os.path.abspath("restore_checkout.py")
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["python", script_path], startupinfo=startupinfo)
        except FileNotFoundError:
            tk.messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{script_path}")

    def start_locker_masterkey(self):
        """[c] 버튼: locker_masterkey.py 실행"""
        script_path = os.path.abspath("locker_masterkey.py")
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(["python", script_path], startupinfo=startupinfo)
        except FileNotFoundError:
            tk.messagebox.showerror("오류", f"파일을 찾을 수 없습니다:\n{script_path}")
    


# ✅ 메인 화면 실행 코드
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
