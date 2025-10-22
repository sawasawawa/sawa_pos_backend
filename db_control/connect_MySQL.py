from sqlalchemy import create_engine

import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')  # .env には 3306 のように数値のみを設定してください
DB_NAME = os.getenv('DB_NAME')

# MySQLのURL構築
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 任意: ルート証明書のパス（不要なら設定しない）
SSL_CA_PATH = os.getenv('SSL_CA_PATH')

engine_kwargs = dict(
    echo=True,
    pool_pre_ping=True,
    pool_recycle=3600,
)

connect_args = {
    "charset": "utf8mb4",
    "autocommit": True,
    "init_command": "SET sql_mode='STRICT_TRANS_TABLES'"
}

if SSL_CA_PATH:
    connect_args["ssl_ca"] = SSL_CA_PATH
else:
    # Azure MySQL用のSSL設定（証明書検証を無効化）
    connect_args["ssl_disabled"] = False
    connect_args["ssl_verify_cert"] = False
    connect_args["ssl_verify_identity"] = False

engine_kwargs["connect_args"] = connect_args

# エンジンの作成
engine = create_engine(DATABASE_URL, **engine_kwargs)
