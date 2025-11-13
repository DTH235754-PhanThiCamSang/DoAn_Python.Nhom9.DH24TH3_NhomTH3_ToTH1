import pyodbc

def connect_db():    
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=LAMVY\\SQLSERVER;"
            "DATABASE=QLNongDuoc;"
            "UID=sa;"
            "PWD=sqlsql;"
            "TrustServerCertificate=yes;"
        )
        print("Kết nối thành công!")
        return conn
    except Exception as e:
        print("Kết nối thất bại:", e)
        return None
connect_db()