import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from tkcalendar import DateEntry
from datetime import date
from connectdb import connect_db
# # ====== Kết nối CSDL ======
# def connect_db():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="123456",
#         database="qltnd"
#     )

# ====== Hàm canh giữa cửa sổ ======
def center_window(win, w=900, h=700):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

# ====== Form Nhà Cung Cấp ======
class FrmNhaCungCap(tk.Toplevel):
    def __init__(self, parent=None, connect_func=connect_db):
        super().__init__(parent)
        self.connect_db = connect_func

        self.title("QUẢN LÝ CỬA HÀNG MUA BÁN THUỐC NÔNG DƯỢC")
        center_window(self, 900, 700)
        self.resizable(False, False)

        lbl_title = tk.Label(self, text="QUẢN LÝ NHÀ CUNG CẤP", font=("Arial", 16, "bold"))
        lbl_title.pack(pady=10)

        # ====== Frame nhập thông tin ======
        f_top = tk.LabelFrame(self, text="Thông tin nhà cung cấp")
        f_top.pack(fill="x", padx=10, pady=5)

        tk.Label(f_top, text="Mã NCC").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.e_mancc = tk.Entry(f_top, width=12)
        self.e_mancc.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(f_top, text="Tên NCC").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.e_tenncc = tk.Entry(f_top, width=35)
        self.e_tenncc.grid(row=0, column=4, padx=5, pady=5, sticky="w")

        tk.Label(f_top, text="Địa chỉ").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.e_diachi = tk.Entry(f_top, width=40)
        self.e_diachi.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        tk.Label(f_top, text="SĐT").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.e_sdt = tk.Entry(f_top, width=15)
        self.e_sdt.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(f_top, text="Email").grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.e_email = tk.Entry(f_top, width=30)
        self.e_email.grid(row=2, column=4, padx=5, pady=5, sticky="w")

        tk.Label(f_top, text="Tìm kiếm").grid(row=3, column=3, padx=5, pady=5, sticky="w")
        self.e_search = tk.Entry(f_top, width=30)
        self.e_search.grid(row=3, column=4, padx=5, pady=5, sticky="w")

        tk.Button(f_top, text="Tải lại", width=8, command=self.luu_data).grid(row=3, column=6, padx=5)

        # ====== Bảng dữ liệu ======
        cols = ("mancc", "tenncc", "diachi", "sodienthoai", "email")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=12)
        for c, t in zip(cols, ["Mã NCC", "Tên nhà cung cấp", "Địa chỉ", "SĐT", "Email"]):
            self.tree.heading(c, text=t)
        self.tree.column("mancc", width=80, anchor="center")
        self.tree.column("tenncc", width=180)
        self.tree.column("diachi", width=200)
        self.tree.column("sodienthoai", width=100, anchor="center")
        self.tree.column("email", width=180)
        self.tree.pack(fill="both", padx=10, pady=5, expand=True)

        # ====== Frame nút ======
        f_btn = tk.Frame(self)
        f_btn.pack(pady=5)

        tk.Button(f_btn, text="Thêm", width=10, command=self.them_ncc).grid(row=0, column=0, padx=5)
        tk.Button(f_btn, text="Lưu", width=10, command=self.luu_ncc).grid(row=0, column=1, padx=5)
        tk.Button(f_btn, text="Sửa", width=10, command=self.sua_ncc).grid(row=0, column=2, padx=5)
        tk.Button(f_btn, text="Xóa", width=10, command=self.xoa_ncc).grid(row=0, column=3, padx=5)
        tk.Button(f_btn, text="Hủy", width=10, command=self.xoa_input).grid(row=0, column=5, padx=5)
        tk.Button(f_btn, text="Thoát", width=10, command=self.destroy).grid(row=0, column=6, padx=5)
        tk.Button(f_top, text="Tìm", width=8, command=self.tim_kiem).grid(row=3, column=5, padx=5, pady=5, sticky="w")

        # Luu dữ liệu và sinh mã đầu tiên
        self.luu_data()
        self.fill_next_mancc()

        self.grab_set()

    # ====== SINH MÃ NCC MỚI ======
    def mancc(self):
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT TOP 1 mancc FROM nhacungcap 
            WHERE mancc LIKE 'NCC%%' 
            ORDER BY mancc DESC 
        """)
        row = cur.fetchone()
        conn.close()

        if not row:
            return "NCC001"

        last_code = row[0]
        num_part = last_code[3:]  # lấy phần số
        try:
            num = int(num_part)
        except:
            num = 0
        num += 1
        return f"NCC{num:03d}"
#điền mã tiep theo tu động
    def fill_next_mancc(self):
        next_code = self.mancc()
        self.e_mancc.delete(0, tk.END)
        self.e_mancc.insert(0, next_code)

    # ====== Các hàm xử lý ======
    def xoa_input(self):
        for e in (self.e_tenncc, self.e_diachi, self.e_sdt, self.e_email, self.e_search):
            e.delete(0, tk.END)
        self.fill_next_mancc()

    def luu_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT mancc, tenncc, diachi, sodienthoai, email FROM nhacungcap ORDER BY mancc ASC")
        for row in cur.fetchall():
            row = list(row)
            row[3] = str(row[3])
            self.tree.insert("", tk.END, values=row)
        conn.close()

    def them_ncc(self):
        mancc = self.e_mancc.get().strip().upper()
        tenncc = self.e_tenncc.get().strip()
        diachi = self.e_diachi.get().strip()
        sdt = self.e_sdt.get().strip()
        email = self.e_email.get().strip()

        if not tenncc:
            messagebox.showwarning("Thiếu dữ liệu", "Phải nhập Tên nhà cung cấp")
            return

        if sdt:
            if not sdt.isdigit():
                messagebox.showwarning("SĐT không hợp lệ", "SĐT chỉ được chứa số")
                return
            if len(sdt) != 10 or not sdt.startswith("0"):
                messagebox.showwarning("SĐT không hợp lệ", "SĐT phải 10 số và bắt đầu bằng 0")
                return

        if email and "@" not in email:
            messagebox.showwarning("Email không hợp lệ", "Email phải có ký tự @")
            return

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO nhacungcap (mancc, tenncc, diachi, sodienthoai, email) VALUES (?,?,?,?,?)",
                (mancc, tenncc, diachi, sdt, email)
            )
            conn.commit()
            conn.close()
            self.luu_data()
            self.xoa_input()
            messagebox.showinfo("Thành công", "Đã thêm nhà cung cấp mới")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def sua_ncc(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Chọn 1 nhà cung cấp để sửa")
            return
        values = self.tree.item(selected)["values"]
        self.e_mancc.delete(0, tk.END)
        self.e_mancc.insert(0, values[0])
        self.e_tenncc.delete(0, tk.END); self.e_tenncc.insert(0, values[1])
        self.e_diachi.delete(0, tk.END); self.e_diachi.insert(0, values[2])
        self.e_sdt.delete(0, tk.END); self.e_sdt.insert(0, str(values[3]))
        self.e_email.delete(0, tk.END); self.e_email.insert(0, values[4])

    def luu_ncc(self):
        mancc = self.e_mancc.get().strip().upper()
        tenncc = self.e_tenncc.get().strip()
        diachi = self.e_diachi.get().strip()
        sdt = self.e_sdt.get().strip()
        email = self.e_email.get().strip()

        if len(sdt) == 9 and sdt.isdigit():
            sdt = "0" + sdt

        if not mancc or not tenncc:
            messagebox.showwarning("Thiếu dữ liệu", "Phải nhập Mã và Tên nhà cung cấp")
            return

        if sdt:
            if not sdt.isdigit():
                messagebox.showwarning("SĐT không hợp lệ", "SĐT chỉ được chứa số")
                return
            if len(sdt) != 10 or not sdt.startswith("0"):
                messagebox.showwarning("SĐT không hợp lệ", "SĐT phải 10 số và bắt đầu bằng 0")
                return

        if email and "@" not in email:
            messagebox.showwarning("Email không hợp lệ", "Email phải có ký tự @")
            return

        try:
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("""
                UPDATE nhacungcap
                SET tenncc=?, diachi=?, sodienthoai=?, email=?
                WHERE mancc=?
            """, (tenncc, diachi, sdt, email, mancc))
            conn.commit()
            conn.close()
            self.luu_data()
            self.xoa_input()
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin nhà cung cấp")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))

    def xoa_ncc(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Chọn 1 nhà cung cấp để xóa")
            return
        mancc = self.tree.item(selected)["values"][0]
        if messagebox.askyesno("Xác nhận", f"Xóa nhà cung cấp {mancc}?"):
            conn = connect_db()
            cur = conn.cursor()
            cur.execute("DELETE FROM nhacungcap WHERE mancc=?", (mancc,))
            conn.commit()
            conn.close()
            self.luu_data()
            self.fill_next_mancc()

    def tim_kiem(self):
        tu_khoa = self.e_search.get().strip()
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT mancc, tenncc, diachi, sodienthoai, email FROM nhacungcap WHERE tenncc LIKE ?",
                    (f"%{tu_khoa}%",))
        for row in cur.fetchall():
            self.tree.insert("", tk.END, values=row)
        conn.close()



if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    FrmNhaCungCap(root)
    root.mainloop()
