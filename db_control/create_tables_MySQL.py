import os
import sys
from pathlib import Path
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
# プロジェクトルート（backend直上）をモジュールパスに追加
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from db_control.mymodels_MySQL import Base, Customers, Items, Purchases, PurchaseDetails
from db_control.connect_MySQL import engine


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

# 商品マスタと購入履歴のサンプルデータを追加
def insert_sample_data():
    Session = sessionmaker(bind=engine)
    session = Session()

    # 商品マスタ（products.jsonから）
    products = [
        {"code": "1234567888", "name": "クルトガシャーペン", "unit_price": 170},
        {"code": "1111122222", "name": "ジェットストリームボールペン", "unit_price": 200},
        {"code": "7492038384", "name": "ゼブラ油性ペン", "unit_price": 120},
        {"code": "37593045739", "name": "MONO消しゴム", "unit_price": 110},
        {"code": "2948560493", "name": "トンボ鉛筆", "unit_price": 60}
    ]

    # 購入履歴（purchases.jsonから）
    purchases = [
        {
            "header": {
                "header_key": 1,
                "cashier_code": "A001",
                "store_code": "30",
                "pos_id": "90",
                "transaction_at": "2025-10-16T08:13:57.842759Z",
                "total_amount": 170
            },
            "details": [
                {
                    "detail_key": 1,
                    "product_code": "1234567888",
                    "product_name": "クルトガシャーペン",
                    "unit_price": 170,
                    "quantity": 1,
                    "line_amount": 170
                }
            ],
            "header_key": 1
        },
        {
            "header": {
                "header_key": 2,
                "cashier_code": "A001",
                "store_code": "30",
                "pos_id": "90",
                "transaction_at": "2025-10-16T08:15:56.348157Z",
                "total_amount": 170
            },
            "details": [
                {
                    "detail_key": 1,
                    "product_code": "1234567888",
                    "product_name": "クルトガシャーペン",
                    "unit_price": 170,
                    "quantity": 1,
                    "line_amount": 170
                }
            ],
            "header_key": 2
        }
    ]

    try:
        # 商品マスタをItemsテーブルに挿入（item_idは商品コードを使用）
        print("Inserting products data...")
        items_data = []
        for p in products:
            items_data.append(Items(
                item_id=p["code"],
                item_name=p["name"],
                price=p["unit_price"]
            ))
        session.add_all(items_data)

        # 購入履歴をPurchases/PurchaseDetailsテーブルに挿入
        print("Inserting purchases data...")
        for i, purchase in enumerate(purchases, 1):
            pur_id = f"PUR{i:03d}"
            purchase_record = Purchases(
                purchase_id=pur_id,
                customer_id="C001",  # デフォルト顧客
                purchase_date=purchase["header"]["transaction_at"][:10]  # YYYY-MM-DD形式
            )
            session.add(purchase_record)

            for j, detail in enumerate(purchase["details"], 1):
                detail_record = PurchaseDetails(
                    detail_id=f"DET{i:03d}{j:02d}",
                    purchase_id=pur_id,
                    item_id=detail["product_code"],  # 商品コード=Items.item_id
                    quantity=detail["quantity"]
                )
                session.add(detail_record)

        session.commit()
        print("Sample data inserted!")
    except Exception as e:
        print(f"Error inserting data: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    init_db()
    insert_sample_data()  # ← ここで呼び出す！
