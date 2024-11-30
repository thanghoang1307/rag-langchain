import sqlite3
import sys

# Lấy đường dẫn thư mục chứa SQLite3
sqlite3_path = sys.modules['sqlite3'].__file__
print("SQLite3 module is located at:", sqlite3_path)

# In ra thông tin chi tiết về thư viện SQLite3
import os
sqlite3_folder = os.path.dirname(sqlite3_path)
print("SQLite3 is located in folder:", sqlite3_folder)

print(sqlite3.sqlite_version)
