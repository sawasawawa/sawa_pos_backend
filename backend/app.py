from fastapi import FastAPI, HTTPException, Query, params
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid
from typing import List, Optional

# データベース関連のインポート
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from db_control.connect_azure import engine
from db_control.mymodels import Items, Purchases, PurchaseDetails, Customers

app = FastAPI()


# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://app-002-gen10-step3-1-node-oshima58.azurewebsites.net",
        "https://*.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# データベースセッションの作成
Session = sessionmaker(bind=engine)

# データのスキーマを定義するためのクラス
class EchoMessage(BaseModel):
    message: str | None = None

class Textdata(BaseModel):
    text: str | None = None

# POSアプリ用のスキーマ
class ItemResponse(BaseModel):
    item_id: str
    item_name: str
    price: int

class CartItem(BaseModel):
    item_id: str
    item_name: str
    price: int
    quantity: int

class PurchaseRequest(BaseModel):
    items: List[CartItem]

class PurchaseResponse(BaseModel):
    purchase_id: str
    total_amount: int
    message: str

@app.get("/")
def hello():
    return {"message": "FastAPI hello!"}

@app.get("/api/hello")
def hello_world():
    return {"message": "Hello!sawa!"}

@app.get("/api/multiply/{id}")
def multiply(id: int):
    print("multiply")
    doubled_value = id * 2
    return {"doubled_value": doubled_value}

@app.get("/api/divide/{id}")
def divide(id: int):
    print("divide")
    divided_value = id / 2
    return {"divided_value": divided_value}

@app.post("/api/characters_count")
def echo(data: Textdata):
    characters_count = len(data.text)
    return {"characters_count": characters_count}

@app.post("/api/echo")
def echo(message: EchoMessage):
    print("echo")
    if not message:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    echo_message = message.message if message.message else "No message provided"
    return {"message": f"echo: {echo_message}"}


# POSアプリケーション用のAPIエンドポイント

# 商品検索API
@app.get("/api/items/{item_code}", response_model=ItemResponse)
def get_item_by_code(item_code: str):
    """商品コードで商品を検索"""
    session = Session()
    try:
        item = session.query(Items).filter(Items.item_id == item_code).first()
        if not item:
            raise HTTPException(status_code=404, detail="商品がマスタ未登録です")
        
        return ItemResponse(
            item_id=item.item_id,
            item_name=item.item_name,
            price=item.price
        )
    finally:
        session.close()

# 購入処理API
@app.post("/api/purchase", response_model=PurchaseResponse)
def process_purchase(purchase_request: PurchaseRequest):
    """購入処理を実行 - 取引明細への登録を含む"""
    session = Session()
    try:
        # 1-1: 取引一意キーを生成
        purchase_id = f"PUR{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 1-1: 取引ヘッダーを作成（取引一意キーを登録）
        purchase = Purchases(
            purchase_id=purchase_id,
            customer_id="C001",  # デフォルト顧客
            purchase_date=datetime.now().strftime('%Y-%m-%d')
        )
        session.add(purchase)
        session.flush()  # 取引一意キーを確定（1-1の登録後の値）
        
        # 1-2: 取引明細へ登録する
        # 合計金額計算用変数
        v_total_amount = 0
        
        # 取引明細一意キー用のインクリメンタル番号
        detail_counter = 1
        
        for item in purchase_request.items:
            # 取引明細一意キー（採番インクリメンタル 1~/取引ごと）
            detail_id = f"DET{purchase_id[-6:]}{detail_counter:02d}"
            
            # 取引明細を作成
            detail = PurchaseDetails(
                detail_id=detail_id,
                purchase_id=purchase_id,  # 取引一意キー（1-1の登録後の値）
                item_id=item.item_id,     # 商品一意キー（パラメータ）
                quantity=item.quantity
            )
            session.add(detail)
            
            # 1-3: 合計を計算する（繰り返し処理）
            # 商品単価を変数"V_合計金額"へ足し込んで合計金額作成
            v_total_amount += item.price * item.quantity
            
            detail_counter += 1
        
        # 1-4: 取引テーブルを更新する
        # 更新条件: 取引一意キー（1-1の登録後の値）
        # 更新値: 合計金額（V_合計金額）
        purchase.total_amount = v_total_amount
        
        session.commit()
        
        return PurchaseResponse(
            purchase_id=purchase_id,
            total_amount=v_total_amount,
            message=f"購入が完了しました。合計金額: {v_total_amount}円"
        )
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"購入処理でエラーが発生しました: {str(e)}")
    finally:
        session.close()

# 商品一覧取得API（管理用）
@app.get("/api/items")
def get_all_items():
    """全商品を取得"""
    session = Session()
    try:
        items = session.query(Items).all()
        return [{"item_id": item.item_id, "item_name": item.item_name, "price": item.price} for item in items]
    finally:
        session.close()

# 購入履歴取得API（管理用）
@app.get("/api/purchases")
def get_purchase_history():
    """購入履歴を取得"""
    session = Session()
    try:
        purchases = session.query(Purchases).order_by(Purchases.purchase_date.desc()).limit(10).all()
        result = []
        for purchase in purchases:
            details = session.query(PurchaseDetails).filter(PurchaseDetails.purchase_id == purchase.purchase_id).all()
            purchase_items = []
            total = 0
            for detail in details:
                item = session.query(Items).filter(Items.item_id == detail.item_id).first()
                if item:
                    line_total = item.price * detail.quantity
                    total += line_total
                    purchase_items.append({
                        "item_name": item.item_name,
                        "quantity": detail.quantity,
                        "price": item.price,
                        "line_total": line_total
                    })
            
            result.append({
                "purchase_id": purchase.purchase_id,
                "purchase_date": purchase.purchase_date,
                "items": purchase_items,
                "total_amount": total
            })
        
        return result
    finally:
        session.close()

# 追加箇所
API_URL = "https://zipcloud.ibsnet.co.jp/api/search"

@app.get("/zipcode/{postal_code}")
def get_address(postal_code: str):
    response = requests.get(API_URL, params={"zipcode": postal_code})
    data = response.json()

# 結果がない場合
    if not data.get("results"):  
        return {"error": data.get("message", "住所情報が見つかりません")}

    return data
