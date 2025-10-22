#!/usr/bin/env python3
"""
環境変数とデータベース接続のテストスクリプト
"""
import os
import sys
from pathlib import Path

# プロジェクトルートをモジュールパスに追加
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# 環境変数を設定
os.environ['PYTHONIOENCODING'] = 'utf-8'

print("=== 環境変数テスト ===")
print(f"DB_USER: {os.getenv('DB_USER', 'Not set')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'Not set'}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'Not set')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'Not set')}")

try:
    from dotenv import load_dotenv
    print("\n=== .envファイル読み込みテスト ===")
    load_dotenv()
    print("✅ .envファイルが正常に読み込まれました")
    
    print(f"DB_USER: {os.getenv('DB_USER', 'Not set')}")
    print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', '')) if os.getenv('DB_PASSWORD') else 'Not set'}")
    print(f"DB_HOST: {os.getenv('DB_HOST', 'Not set')}")
    print(f"DB_PORT: {os.getenv('DB_PORT', 'Not set')}")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'Not set')}")
    
except Exception as e:
    print(f"❌ .envファイルの読み込みに失敗: {e}")

try:
    print("\n=== データベース接続テスト ===")
    from db_control.connect_MySQL import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"✅ データベース接続成功! テスト結果: {row[0]}")
        
except Exception as e:
    print(f"❌ データベース接続エラー: {e}")
    print(f"エラータイプ: {type(e).__name__}")
