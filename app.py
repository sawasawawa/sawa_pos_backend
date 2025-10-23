from fastapi import FastAPI, HTTPException, Query, params
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import sessionmaker
from db_control import crud, mymodels
from db_control.connect import engine as sqlite_engine
from db_control.mymodels import Items, Purchases, PurchaseDetails


app = FastAPI()


# CORSの設定 フロントエンドからの接続を許可する部分
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://app-002-gen10-step3-1-node-oshima58.azurewebsites.net"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ===== POS 用のモデル =====
class Product(BaseModel):
    code: str
    name: str
    unit_price: int

class PurchaseItem(BaseModel):
    code: str
    name: str
    unit_price: int
    quantity: int

class ProductLookupResponse(BaseModel):
    product: Optional[Product] | None

class PurchaseCommitItem(BaseModel):
    product_code: str
    product_name: str
    unit_price: int
    quantity: int

class PurchaseCommitRequest(BaseModel):
    items: List[PurchaseCommitItem]

class PurchaseCommitResponse(BaseModel):
    success: bool
    total_amount: int
    header_key: int

# 取引参照系のDTO/エンドポイントは削除してシンプル化

@app.get("/")
def hello():
    return {"message": "POS backend"}


# 住所検索などのデモAPIは削除し、シンプルに維持


# ====== POS: データアクセス（SQLite） ======
SessionSQLite = sessionmaker(bind=sqlite_engine)


# 旧デモAPI（/api/products, /api/purchase）は削除


# ========= 仕様準拠エンドポイント =========
@app.get("/api/product", response_model=ProductLookupResponse)
def product_lookup(code: str):
    """機能名: 商品マスタ検索
    - パラメータ: code
    - リターン: 商品情報 1 件。未登録時は product=null を返す
    """
    with SessionSQLite() as s:
        item = s.query(Items).filter(Items.item_id == code).first()
        if not item:
            return {"product": None}
        return {"product": {"code": item.item_id, "name": item.item_name, "unit_price": item.price}}


@app.post("/api/purchase/commit", response_model=PurchaseCommitResponse)
def purchase_commit(req: PurchaseCommitRequest):
    """機能名: 購入
    1-1 取引ヘッダ登録
    1-2 取引明細登録
    1-3 合計算出
    1-4 取引ヘッダ更新
    1-5 合計金額をレスポンス返却（SQLiteへ保存）
    """
    if not req.items:
        raise HTTPException(status_code=400, detail="明細がありません")

    # DBへ保存
    with SessionSQLite() as s:
        total = 0
        # Purchasesに挿入
        trd_id = f"PUR{int(datetime.utcnow().timestamp())}"
        pur = Purchases(purchase_id=trd_id, customer_id="C001", purchase_date=datetime.utcnow().strftime("%Y-%m-%d"), total_amount=0)
        s.add(pur)
        s.flush()

        # 明細
        for idx, it in enumerate(req.items, 1):
            subtotal = it.unit_price * it.quantity
            total += subtotal
            det = PurchaseDetails(
                detail_id=f"DET{trd_id}{idx:02d}",
                purchase_id=trd_id,
                item_id=it.product_code,
                quantity=it.quantity,
                unit_price=it.unit_price,
                subtotal=subtotal
            )
            s.add(det)

        # 合計金額を更新
        pur.total_amount = total
        s.commit()
        return PurchaseCommitResponse(success=True, total_amount=total, header_key=trd_id)


# SQLiteの定義は不要になったため削除


# 取引参照APIは要求により削除
