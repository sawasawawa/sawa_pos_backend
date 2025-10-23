from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Azure App Service用の設定
load_dotenv()

# Azure App Service環境変数から取得、なければローカル設定を使用
DB_USER = os.getenv('DB_USER', 'tech0gen10student')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'vY7JZNfU')
DB_HOST = os.getenv('DB_HOST', 'dbs-002-gen10-step3-2-oshima5.mysql.database.azure.com')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'sawa_pos')

# Azure MySQL用の接続文字列
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Azure MySQL用のSSL設定
engine_kwargs = {
    "connect_args": {
        "ssl": {
            "ssl_ca": "/home/site/wwwroot/DigiCertGlobalRootG2.crt.pem"
        }
    }
}

# ローカル環境の場合はSQLiteを使用
if os.getenv('WEBSITE_SITE_NAME') is None:  # ローカル環境
    import platform
    main_path = os.path.dirname(os.path.abspath(__file__))
    path = os.chdir(main_path)
    engine = create_engine("sqlite:///CRM.db", echo=True)
else:  # Azure App Service環境
    engine = create_engine(DATABASE_URL, **engine_kwargs)
