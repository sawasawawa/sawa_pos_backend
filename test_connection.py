#!/usr/bin/env python3
import sys
from pathlib import Path

# プロジェクトルートをモジュールパスに追加
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

try:
    from db_control.connect_MySQL import engine
    from sqlalchemy import text
    
    print("MySQL接続テスト開始...")
    
    # 接続テスト
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        print(f"接続成功! テスト結果: {row[0]}")
        
        # データベース一覧表示
        result = conn.execute(text("SHOW DATABASES"))
        databases = [row[0] for row in result.fetchall()]
        print(f"利用可能なデータベース: {databases}")
        
except Exception as e:
    print(f"接続エラー: {e}")
    print(f"エラータイプ: {type(e).__name__}")
