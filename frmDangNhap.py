import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import hashlib
import mysql.connector

# ====== Kết nối MySQL ======
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="qltnd"   
    )

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=800, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f'{w}x{h}+{x}+{y}')

# Mã hóa mật khẩu mà người dùng nhập
PLAINTEXT_PASSWORD_IN_DB = False

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class DangNhap(tk.Toplevel):
    def __init__(self, parent=None, on_success=None):
        super().__init__(parent)
        self.parent = parent
        self.on_success = on_success

        self.title("Đăng nhập hệ thống")
        center_window(self, 420, 260)
        self.resizable(False, False)
        self.TaoUI()
        self.bind("<Return>", lambda e: self.dangnhap()) #dùng phím Enter để đăng nhập

        
        self.grab_set()
        self.focus()

    

    

    def TaoUI(self):
        frm = ttk.Frame(self, padding=16)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="ĐĂNG NHẬP", font=("Tahoma", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(0, 10)
        )

        ttk.Label(frm, text="Tên đăng nhập:").grid(row=1, column=0, sticky="e", padx=(0, 8), pady=6)
        self.txt_user = ttk.Entry(frm, width=28)
        self.txt_user.grid(row=1, column=1, columnspan=2, sticky="we")
        self.txt_user.focus()

        ttk.Label(frm, text="Mật khẩu:").grid(row=2, column=0, sticky="e", padx=(0, 8), pady=6)
        self.var_pwd = tk.StringVar()
        self.txt_pwd = ttk.Entry(frm, width=28, textvariable=self.var_pwd, show="*")
        self.txt_pwd.grid(row=2, column=1, columnspan=2, sticky="we")

        self.var_show = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frm,
            text="Hiện mật khẩu",
            variable=self.var_show,
            command=lambda: self.txt_pwd.config(show="" if self.var_show.get() else "*")
        ).grid(row=3, column=1, sticky="w", pady=(0, 8))

        ttk.Button(frm, text="Đăng nhập", command=self.dangnhap).grid(row=4, column=1, sticky="we", padx=(0, 6))
        ttk.Button(frm, text="Quên mật khẩu", command=self.quenmatkhau).grid(row=4, column=2, sticky="we")
        ttk.Button(frm, text="Thoát", command=self.thoat).grid(row=5, column=2, sticky="e", pady=(16, 0))

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(2, weight=1)

    # ----------------- DB  -----------------
    def ktrataikhoan(self, username: str, password: str):
       
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT password_hash, full_name FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            messagebox.showerror("Lỗi MySQL", f"Không thể truy vấn người dùng.\n{e}")
            return False, None

        if not row:
            return False, None

        db_pwd_hash, full_name = row
        if PLAINTEXT_PASSWORD_IN_DB:
            ok = (password == db_pwd_hash)
        else:
            ok = (sha256(password) == db_pwd_hash)

        return (ok, full_name if ok else None)

    def cauhoibaomat(self, username: str):
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT security_question FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            messagebox.showerror("Lỗi MySQL", f"Không thể lấy câu hỏi bảo mật.\n{e}")
            return None

    def xacminhcautraloi(self, username: str, answer: str) -> bool:
        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("SELECT security_answer_hash FROM users WHERE username=?", (username,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return False
            return sha256(answer.strip()) == row[0]
        except Exception as e:
            messagebox.showerror("Lỗi MySQL", f"Lỗi xác minh câu trả lời.\n{e}")
            return False

    def capnhatmatkhau(self, username: str, new_password: str):
        try:
            conn = connect_db()
            cur = conn.cursor()
            new_hash = new_password if PLAINTEXT_PASSWORD_IN_DB else sha256(new_password)
            cur.execute("UPDATE users SET password_hash=? WHERE username=?", (new_hash, username))
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Lỗi MySQL", f"Không thể cập nhật mật khẩu.\n{e}")
            return False

    # ----------------- Events -----------------
    def dangnhap(self):
        u = self.txt_user.get().strip()
        p = self.var_pwd.get()
        if not u or not p:
            messagebox.showinfo("Thiếu thông tin", "Vui lòng nhập Tên đăng nhập và Mật khẩu.")
            return
        ok, full_name = self.ktrataikhoan(u, p)
        if ok:
            messagebox.showinfo("Thành công", f"Xin chào {full_name or u}!\nĐăng nhập thành công.")

            # GỌI MỞ MENU 
            from main import show_menu  
            self.destroy()
            show_menu() 
            
            

        else:
            messagebox.showerror("Sai thông tin", "Tên đăng nhập hoặc mật khẩu không đúng.")

    def quenmatkhau(self):
        username = simpledialog.askstring("Quên mật khẩu", "Nhập Tên đăng nhập:", parent=self)
        if not username:
            return
        question = self.cauhoibaomat(username)
        if not question:
            messagebox.showerror("Lỗi", "Không tìm thấy người dùng hoặc chưa có câu hỏi bảo mật.")
            return
        answer = simpledialog.askstring("Xác minh", question, parent=self)
        if answer is None:
            return
        if not self.xacminhcautraloi(username, answer):
            messagebox.showerror("Sai câu trả lời", "Câu trả lời bảo mật không đúng.")
            return
        new_pwd = simpledialog.askstring("Đổi mật khẩu", "Nhập mật khẩu mới (>= 6 ký tự):", show="*", parent=self)
        if not new_pwd:
            return
        if len(new_pwd) < 6:
            messagebox.showwarning("Yêu cầu", "Mật khẩu phải từ 6 ký tự trở lên.")
            return
        if self.capnhatmatkhau(username, new_pwd):
            messagebox.showinfo("Hoàn tất", "Đổi mật khẩu thành công!")

    def thoat(self):
        if self.parent is not None:
            self.parent.destroy()
        else:
            self.destroy()


def main():
    root = tk.Tk()
    root.withdraw()     
    DangNhap(parent=root)
    root.mainloop()
   
if __name__ == "__main__":
    main()
