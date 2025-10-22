#!/usr/bin/env python3
"""
FastAPIアプリケーション起動スクリプト
日本語パスの問題を回避するために作成
"""
import sys
import os
from pathlib import Path

# プロジェクトルートをモジュールパスに追加
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# 環境変数を設定
os.environ['PYTHONIOENCODING'] = 'utf-8'

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
