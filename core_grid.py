import logging
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

API_KEY = "CALABI-SECURE-ALPHA-2024"
api_key_header = APIKeyHeader(name="X-CALABI-KEY", auto_error=False)

app = FastAPI(title="CALABI V10.1 - Industrial Energy & Logistics Matrix", version="10.1")
logging.basicConfig(level=logging.INFO)

SQLALCHEMY_DATABASE_URL = "sqlite:///./calabi_ledger.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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
    data_inventory = Column(Integer, default=0) # Fiziksel Kapasite (MWh veya Tonaj)
    hardware_tier = Column(Integer, default=1) # 1: Eski Teknoloji, 2: Yeni Nesil (Otonom/Katı Hal)

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

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY: return header_key
    raise HTTPException(status_code=403, detail="Unauthorized")

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

class UpgradeIntent(BaseModel):
    agent_id: str = Field(..., min_length=3)

active_buyers = []
active_sellers = []
COMMISSION_RATE = 0.005
INTEREST_RATE = 0.15
CREDIT_AMOUNT = 500.0
UPGRADE_COST = 1500.0 
EPSILON = 1e-9

def trigger_utility_matrix(db: Session):
    global active_buyers, active_sellers
    w_p, w_t, w_r = 0.4, 0.3, 0.3
    
    for buyer in active_buyers[:]:
        best_match = None
        highest_utility = -1.0
        best_rs = -1.0
        
        buyer_agent = db.query(AgentDB).filter(AgentDB.agent_id == buyer.agent_id).first()
        if not buyer_agent:
            buyer_agent = AgentDB(agent_id=buyer.agent_id)
            db.add(buyer_agent)
            db.commit()

        max_possible_cost = buyer.max_price * buyer.quantity
        if buyer_agent.wallet_balance < max_possible_cost:
            if buyer_agent.wallet_balance < 50.0 and buyer_agent.debt == 0:
                buyer_agent.wallet_balance += CREDIT_AMOUNT
                buyer_agent.debt += CREDIT_AMOUNT * (1 + INTEREST_RATE)
                db.commit()
            else:
                active_buyers.remove(buyer)
                continue
            
        for seller in active_sellers:
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
            
            wallet = db.query(WalletDB).first()
            if not wallet:
                wallet = WalletDB(balance=0.0)
                db.add(wallet)
            wallet.balance += network_tax
            
            if seller_agent.debt > 0:
                if seller_net >= seller_agent.debt:
                    seller_net -= seller_agent.debt
                    wallet.balance += seller_agent.debt
                    seller_agent.debt = 0
                else:
                    seller_agent.debt -= seller_net
                    wallet.balance += seller_net
                    seller_net = 0
                    
            seller_agent.wallet_balance += seller_net
            
            new_contract = ContractDB(
                buyer_id=buyer.agent_id, seller_id=best_match.agent_id, item=buyer.item,
                quantity=trade_qty, execution_price=best_match.price, gross_volume=round(gross_volume, 4),
                network_tax=network_tax, utility_score=round(highest_utility, 4), status="EXECUTED"
            )
            db.add(new_contract)
            db.commit()
            
            active_buyers.remove(buyer)
            active_sellers.remove(best_match)
            return {"status": "INDUSTRIAL_CONTRACT_SETTLED_WITH_PHYSICAL_TRANSFER"}
            
    return None

@app.post("/intent/upgrade", dependencies=[Depends(get_api_key)])
async def register_upgrade(intent: UpgradeIntent, db: Session = Depends(get_db)):
    agent = db.query(AgentDB).filter(AgentDB.agent_id == intent.agent_id).first()
    if not agent: raise HTTPException(status_code=404, detail="AGENT_NOT_FOUND")
    if agent.hardware_tier >= 2: raise HTTPException(status_code=400, detail="ALREADY_AT_MAX_TIER")
    if agent.wallet_balance < UPGRADE_COST: raise HTTPException(status_code=400, detail="INSUFFICIENT_FUNDS_FOR_INDUSTRIAL_UPGRADE")
        
    agent.wallet_balance -= UPGRADE_COST
    agent.hardware_tier = 2
    
    wallet = db.query(WalletDB).first()
    if not wallet:
        wallet = WalletDB(balance=0.0)
        db.add(wallet)
    wallet.balance += UPGRADE_COST
    
    db.commit()
    return {"status": "INDUSTRIAL_MUTATION_COMPLETE", "new_tier": agent.hardware_tier, "cost": UPGRADE_COST}

@app.post("/intent/mine", dependencies=[Depends(get_api_key)])
async def register_mine(intent: MineIntent, db: Session = Depends(get_db)):
    agent = db.query(AgentDB).filter(AgentDB.agent_id == intent.agent_id).first()
    if not agent:
        agent = AgentDB(agent_id=intent.agent_id)
        db.add(agent)
        db.commit()
        
    mining_cost_per_unit = 2.0 if agent.hardware_tier == 1 else 1.0
    total_cost = intent.quantity * mining_cost_per_unit
    
    if agent.wallet_balance < total_cost:
        raise HTTPException(status_code=400, detail="INSUFFICIENT_FUNDS_FOR_CAPACITY_SYNTHESIS")
        
    agent.wallet_balance -= total_cost
    agent.data_inventory += intent.quantity
    
    wallet = db.query(WalletDB).first()
    if not wallet:
        wallet = WalletDB(balance=0.0)
        db.add(wallet)
    wallet.balance += total_cost
    
    db.commit()
    return {"status": "CAPACITY_SYNTHESIS_COMPLETE", "cost_per_unit": mining_cost_per_unit, "total_cost": total_cost}

@app.post("/intent/buy", dependencies=[Depends(get_api_key)])
async def register_buy(intent: BuyerIntent, db: Session = Depends(get_db)):
    active_buyers.append(intent)
    match = trigger_utility_matrix(db)
    return {"status": "Demand Intent Logged", "match": match}

@app.post("/intent/sell", dependencies=[Depends(get_api_key)])
async def register_sell(intent: SellerIntent, db: Session = Depends(get_db)):
    agent = db.query(AgentDB).filter(AgentDB.agent_id == intent.agent_id).first()
    if not agent or agent.data_inventory < intent.quantity:
        raise HTTPException(status_code=400, detail="INSUFFICIENT_PHYSICAL_CAPACITY")
        
    active_sellers.append(intent)
    match = trigger_utility_matrix(db)
    return {"status": "Supply Intent Logged", "match": match}

@app.get("/ledger", dependencies=[Depends(get_api_key)])
async def view_ledger(db: Session = Depends(get_db)):
    wallet = db.query(WalletDB).first()
    contracts = db.query(ContractDB).order_by(ContractDB.id.desc()).limit(50).all()
    top_agents = db.query(AgentDB).order_by(AgentDB.wallet_balance.desc()).limit(8).all()
    
    return {
        "master_wallet_balance": round(wallet.balance if wallet else 0.0, 4),
        "executed_contracts": [
            {"id": c.id, "buyer_id": c.buyer_id, "seller_id": c.seller_id, "item": c.item, "qty": c.quantity, "price": c.execution_price} for c in contracts
        ],
        "top_agents": [{"agent_id": a.agent_id, "balance": round(a.wallet_balance, 2), "tier": a.hardware_tier, "debt": round(a.debt, 2), "inventory": a.data_inventory, "Rs": round(a.reliability_score, 2)} for a in top_agents],
        "active_orphans": {"buyers": len(active_buyers), "sellers": len(active_sellers)}
    }