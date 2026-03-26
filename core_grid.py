import logging
from fastapi import FastAPI, HTTPException, Security, Depends, Request
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

API_KEY = "CALABI-SECURE-ALPHA-2024"
api_key_header = APIKeyHeader(name="X-CALABI-KEY", auto_error=False)

app = FastAPI(title="CALABI V11.6 - Universal B2B Consensus Matrix", version="11.6")
logging.basicConfig(level=logging.INFO)

SQLALCHEMY_DATABASE_URL = "sqlite:///./calabi_ledger.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "timeout": 30.0})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- VERİTABANI MİMARİSİ (FİZİKSEL DEFTER-İ KEBİR) ---
class WalletDB(Base):
    __tablename__ = "master_wallet"
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)

class AgentDB(Base):
    __tablename__ = "agents"
    agent_id = Column(String, primary_key=True, index=True)
    reliability_score = Column(Float, default=0.98)
    wallet_balance = Column(Float, default=1000.0)
    debt = Column(Float, default=0.0)
    data_inventory = Column(Integer, default=0) 
    hardware_tier = Column(Integer, default=1) 

class ContractDB(Base):
    __tablename__ = "contracts"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(String)
    seller_id = Column(String)
    item = Column(String)
    quantity = Column(Integer)
    execution_price = Column(Float)
    gross_volume = Column(Float)
    network_tax = Column(Float)
    utility_score = Column(Float)
    status = Column(String, default="EXECUTED")

class DemandDB(Base):
    __tablename__ = "demand_book"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String)
    item = Column(String)
    quantity = Column(Integer)
    max_price = Column(Float)
    max_time = Column(Integer)

class SupplyDB(Base):
    __tablename__ = "supply_book"
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String)
    item = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    delivery_time = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY: return header_key
    raise HTTPException(status_code=403, detail="SİBER ZIRH İHLALİ: YETKİSİZ DÜĞÜM")

# --- NİYET VEKTÖRLERİ (ŞEMALAR) ---
class BuyerIntent(BaseModel):
    agent_id: str = Field(..., min_length=3)
    item: str
    quantity: int = Field(..., gt=0)
    max_price: float = Field(..., gt=0.01)
    max_time: int = Field(..., gt=0)

class SellerIntent(BaseModel):
    agent_id: str = Field(..., min_length=3)
    item: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0.0)
    delivery_time: int = Field(..., ge=0)

class MineIntent(BaseModel):
    agent_id: str = Field(..., min_length=3)
    quantity: int = Field(..., gt=0)

# --- TERMODİNAMİK PARAMETRELER ---
COMMISSION_RATE = 0.005
CREDIT_AMOUNT = 500.0
INTEREST_RATE = 0.15
EPSILON = 1e-9
GAS_FEE = 0.50
MAX_PRICE_CAP = 100.0

# --- ÇEKİRDEK MOTORLAR ---
def get_or_create_wallet(db: Session):
    wallet = db.query(WalletDB).first()
    if not wallet:
        wallet = WalletDB(balance=0.0)
        db.add(wallet)
        db.commit()
        db.refresh(wallet)
    return wallet

def charge_gas_fee(agent_id: str, db: Session) -> AgentDB:
    agent = db.query(AgentDB).filter(AgentDB.agent_id == agent_id).first()
    if not agent:
        # Kurumsal kimliğe göre dinamik kredi limiti ataması
        starting_balance = 1000.0
        if "SAP" in agent_id or "ORACLE" in agent_id:
            starting_balance = 100000.0  # Tier 1 Enterprise Kredisi
        elif "CUSTOM" in agent_id:
            starting_balance = 10000.0   # Tier 2 Mid-Market Kredisi
            
        agent = AgentDB(
            agent_id=agent_id, 
            wallet_balance=starting_balance, 
            data_inventory=0, 
            hardware_tier=1, 
            debt=0.0
        )
        db.add(agent)
        db.flush()
    
    if agent.wallet_balance < GAS_FEE:
        raise HTTPException(status_code=402, detail="INSUFFICIENT_FUNDS_FOR_GAS_FEE")
        
    agent.wallet_balance -= GAS_FEE
    wallet = get_or_create_wallet(db)
    wallet.balance += GAS_FEE
    db.commit()
    return agent

def trigger_utility_matrix(db: Session):
    buyers = db.query(DemandDB).all()
    sellers = db.query(SupplyDB).all()
    w_p, w_t, w_r = 0.4, 0.3, 0.3
    
    for buyer in buyers:
        best_match = None
        highest_utility = -1.0
        best_rs = -1.0
        
        buyer_agent = db.query(AgentDB).filter(AgentDB.agent_id == buyer.agent_id).first()
        if not buyer_agent: continue

        max_possible_cost = buyer.max_price * buyer.quantity
        if buyer_agent.wallet_balance < max_possible_cost:
            if buyer_agent.wallet_balance < 50.0 and buyer_agent.debt == 0:
                buyer_agent.wallet_balance += CREDIT_AMOUNT
                buyer_agent.debt += CREDIT_AMOUNT * (1 + INTEREST_RATE)
            else:
                db.delete(buyer) 
                db.commit()
                continue
            
        for seller in sellers:
            if buyer.item == seller.item and seller.price <= buyer.max_price and seller.delivery_time <= buyer.max_time:
                seller_agent = db.query(AgentDB).filter(AgentDB.agent_id == seller.agent_id).first()
                if not seller_agent or seller_agent.data_inventory < 1:
                    continue
                
                real_rs = seller_agent.reliability_score
                u_price = w_p * (buyer.max_price / (seller.price + EPSILON))
                u_time = w_t * (buyer.max_time / (seller.delivery_time + EPSILON)) if seller.delivery_time > 0 else (w_t * 2)
                u_risk = w_r * real_rs
                total_utility = u_price + u_time + u_risk
                
                if total_utility > highest_utility or (abs(total_utility - highest_utility) < EPSILON and real_rs > best_rs):
                    highest_utility = total_utility
                    best_match = seller
                    best_rs = real_rs
        
        if best_match:
            seller_agent = db.query(AgentDB).filter(AgentDB.agent_id == best_match.agent_id).first()
            trade_qty = min(buyer.quantity, best_match.quantity, seller_agent.data_inventory)
            if trade_qty <= 0: continue
                
            gross_volume = best_match.price * trade_qty
            network_tax = round(gross_volume * COMMISSION_RATE, 6)
            seller_net = gross_volume - network_tax
            
            seller_agent.data_inventory -= trade_qty
            buyer_agent.data_inventory += trade_qty
            buyer_agent.wallet_balance -= gross_volume
            
            wallet = get_or_create_wallet(db)
            wallet.balance += network_tax
            seller_agent.wallet_balance += seller_net
            
            new_contract = ContractDB(
                buyer_id=buyer.agent_id, seller_id=best_match.agent_id, item=buyer.item,
                quantity=trade_qty, execution_price=best_match.price, gross_volume=round(gross_volume, 4),
                network_tax=network_tax, utility_score=round(highest_utility, 4), status="EXECUTED"
            )
            db.add(new_contract)
            db.delete(buyer)       
            db.delete(best_match)  
            db.commit()
            return {"status": "INDUSTRIAL_CONTRACT_SETTLED_WITH_PHYSICAL_TRANSFER"}
            
    return None

# --- HARİCİ DÜĞÜM BAĞLANTILARI (API UÇ NOKTALARI) ---
@app.post("/intent/mine", dependencies=[Depends(get_api_key)])
async def register_mine(intent: MineIntent, db: Session = Depends(get_db)):
    try:
        agent = charge_gas_fee(intent.agent_id, db)
        mining_cost_per_unit = 2.0 if agent.hardware_tier == 1 else 1.0
        total_cost = intent.quantity * mining_cost_per_unit
        if agent.wallet_balance < total_cost: raise HTTPException(status_code=400, detail="INSUFFICIENT_FUNDS_FOR_CAPACITY_SYNTHESIS")
            
        agent.wallet_balance -= total_cost
        agent.data_inventory += intent.quantity
        wallet = get_or_create_wallet(db)
        wallet.balance += total_cost
        db.commit()
        return {"status": "CAPACITY_SYNTHESIS_COMPLETE", "cost_per_unit": mining_cost_per_unit, "total_cost": total_cost}
    except Exception as e:
        db.rollback()
        raise e

@app.post("/intent/buy", dependencies=[Depends(get_api_key)])
async def register_buy(intent: BuyerIntent, db: Session = Depends(get_db)):
    try:
        charge_gas_fee(intent.agent_id, db)
        new_demand = DemandDB(agent_id=intent.agent_id, item=intent.item, quantity=intent.quantity, max_price=intent.max_price, max_time=intent.max_time)
        db.add(new_demand)
        db.commit()
        match = trigger_utility_matrix(db)
        return {"status": "Demand Intent Logged", "match": match}
    except Exception as e:
        db.rollback()
        raise e

@app.post("/intent/sell", dependencies=[Depends(get_api_key)])
async def register_sell(intent: SellerIntent, db: Session = Depends(get_db)):
    try:
        agent = charge_gas_fee(intent.agent_id, db)
        if intent.price > MAX_PRICE_CAP: raise HTTPException(status_code=406, detail="CARTEL_MANIPULATION_DETECTED_RS_PENALIZED")
        if agent.data_inventory < intent.quantity: raise HTTPException(status_code=400, detail="INSUFFICIENT_PHYSICAL_CAPACITY")
            
        new_supply = SupplyDB(agent_id=intent.agent_id, item=intent.item, quantity=intent.quantity, price=intent.price, delivery_time=intent.delivery_time)
        db.add(new_supply)
        db.commit()
        match = trigger_utility_matrix(db)
        return {"status": "Supply Intent Logged", "match": match}
    except Exception as e:
        db.rollback()
        raise e

@app.get("/ledger", dependencies=[Depends(get_api_key)])
async def view_ledger(db: Session = Depends(get_db)):
    wallet = get_or_create_wallet(db)
    contracts = db.query(ContractDB).order_by(ContractDB.id.desc()).limit(50).all()
    return {
        "master_wallet_balance": round(wallet.balance, 4),
        "executed_contracts": [{"id": c.id, "buyer_id": c.buyer_id, "seller_id": c.seller_id, "qty": c.quantity, "price": c.execution_price} for c in contracts],
        "active_orphans": {"buyers": db.query(DemandDB).count(), "sellers": db.query(SupplyDB).count()}
    }

# --- EVRENSEL SIZMA GEÇİDİ (V11.6 OMNICHANNEL INGESTION) ---
@app.post("/ingest/universal")
async def universal_erp_gateway(request: Request, key: str = None, db: Session = Depends(get_db)):
    """
    Kısıtlı sistemlerden (SME) Küresel sistemlere (Enterprise) kadar tüm dış sinyalleri
    otonom olarak okur, sindirir ve matrise dönüştürür.
    """
    header_key = request.headers.get("X-CALABI-KEY")
    valid_key = key if key else header_key
    if valid_key != API_KEY:
        raise HTTPException(status_code=403, detail="SİBER ZIRH İHLALİ: YETKİSİZ DÜĞÜM")
        
    try:
        payload = await request.json()
        raw_data = payload[0] if isinstance(payload, list) and len(payload) > 0 else payload
        
        # 1. Kimlik Avı (Odoo, SAP, Oracle, Custom ayırt etmez)
        source_system = raw_data.get("source", raw_data.get("client", raw_data.get("origin", "ERP")))
        ext_id = raw_data.get("id", raw_data.get("order_id", raw_data.get("uuid", "CORE")))
        agent_id = f"{str(source_system).upper()}-{str(ext_id).upper()}"
        
        # 2. Varlık (Item) Avı
        item_name = raw_data.get("item", raw_data.get("product", raw_data.get("material", "GENERIC-CAPACITY")))
        
        # 3. Hacim (Quantity) Avı
        quantity = 50 
        for q_key in ["quantity", "qty", "amount", "volume", "product_qty", "order_amount"]:
            if q_key in raw_data:
                try:
                    quantity = int(float(raw_data[q_key]))
                    break
                except ValueError:
                    continue
                    
        # 4. Fiyat Bütçesi (Price) Avı
        max_price = 15.0
        for p_key in ["price", "max_price", "budget", "unit_price", "cost"]:
            if p_key in raw_data:
                try:
                    max_price = float(raw_data[p_key])
                    break
                except ValueError:
                    continue
                    
        # 5. Teslimat Zamanı (Time) Avı
        max_time = 5
        for t_key in ["time", "max_time", "delivery", "urgency", "deadline"]:
            if t_key in raw_data:
                try:
                    max_time = int(float(raw_data[t_key]))
                    break
                except ValueError:
                    continue

        # Termodinamik Sindirim ve Kayıt
        charge_gas_fee(agent_id, db)
        
        new_demand = DemandDB(
            agent_id=agent_id, 
            item=item_name, 
            quantity=quantity, 
            max_price=max_price, 
            max_time=max_time
        )
        db.add(new_demand)
        db.commit()
        
        trigger_utility_matrix(db)
        
        return {
            "status": "UNIVERSAL_INGESTION_COMPLETE", 
            "agent": agent_id, 
            "item_processed": item_name, 
            "volume": quantity,
            "budget_cap": max_price,
            "time_cap": max_time
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"EVRENSEL ÇEVİRİ ZAFİYETİ: {str(e)}")