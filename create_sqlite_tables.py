import os
import sys
from pathlib import Path
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# プロジェクトルート（backend直上）をモジュールパスに追加
ROOT_DIR = Path(__file__).resolve().parents[0]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from db_control.mymodels import Base, Customers, Items, Purchases, PurchaseDetails
from db_control.connect import engine

def init_db():
    # インスペクターを作成
    inspector = inspect(engine)

    # 既存のテーブルを取得
    existing_tables = inspector.get_table_names()

    print("Checking tables...")

    # customersテーブルが存在しない場合は作成
    if 'customers' not in existing_tables:
        print("Creating tables >>> ")
        try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully!")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise
    else:
        print("Tables already exist.")

# 商品マスタとサンプルデータを追加
def insert_sample_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    # 商品マスタのサンプルデータ
    products = [
        {"code": "1234567888", "name": "クルトガシャーペン", "unit_price": 170},
        {"code": "1111122222", "name": "ジェットストリームボールペン", "unit_price": 200},
        {"code": "7492038384", "name": "ゼブラ油性ペン", "unit_price": 120},
        {"code": "37593045739", "name": "MONO消しゴム", "unit_price": 110},
        {"code": "2948560493", "name": "トンボ鉛筆", "unit_price": 60},
        {"code": "12345678901", "name": "おーいお茶", "unit_price": 150},
        {"code": "98765432109", "name": "ソフラン", "unit_price": 300},
        {"code": "55555555555", "name": "福島産ほうれん草", "unit_price": 188},
        {"code": "77777777777", "name": "タイガー歯ブラシ青", "unit_price": 200},
        {"code": "99999999999", "name": "四ツ谷サイダー", "unit_price": 160}
    ]

    try:
        # デフォルト顧客を作成
        print("Creating default customer...")
        default_customer = Customers(
            customer_id="C001",
            customer_name="一般顧客",
            age=30,
            gender="その他"
        )
        session.add(default_customer)

        # 商品マスタをItemsテーブルに挿入
        print("Inserting products data...")
        items_data = []
        for p in products:
            items_data.append(Items(
                item_id=p["code"],
                item_name=p["name"],
                price=p["unit_price"]
            ))
        session.add_all(items_data)

        session.commit()
        print("Sample data inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    insert_sample_data()
