import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

print(f"Connecting to: {DB_HOST}:{DB_PORT}")
print(f"Database: {DB_NAME}")
print(f"User: {DB_USER}")

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SSL設定
connect_args = {
    "charset": "utf8mb4",
    "autocommit": True,
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
    "ssl_disabled": False,
    "ssl_verify_cert": False,
    "ssl_verify_identity": False
}

# SSL証明書のパスを設定
ssl_ca_path = os.path.join(os.getcwd(), "DigiCertGlobalRootG2.crt.pem")
if os.path.exists(ssl_ca_path):
    connect_args["ssl_ca"] = ssl_ca_path
    print(f"Using SSL certificate: {ssl_ca_path}")
else:
    print("SSL certificate not found, using default SSL settings")

engine_kwargs = {
    "echo": True,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "connect_args": connect_args
}

try:
    print("\nCreating engine...")
    engine = create_engine(DATABASE_URL, **engine_kwargs)
    
    print("Testing connection...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"Connection successful! Test query result: {row[0]}")
        
        # データベースのテーブル一覧を取得
        print("\nChecking existing tables...")
        result = connection.execute(text("SHOW TABLES"))
        tables = result.fetchall()
        if tables:
            print("Existing tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("No tables found in database")
            
except Exception as e:
    print(f"Connection failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # より詳細なエラー情報
    if hasattr(e, 'orig'):
        print(f"Original error: {e.orig}")
    
    # 接続URL（パスワードを隠す）
    safe_url = DATABASE_URL.replace(DB_PASSWORD, "***")
    print(f"Connection URL: {safe_url}")
