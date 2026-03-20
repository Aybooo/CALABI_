import logging
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# 1. CORE CONFIGURATION & SECURITY
API_KEY = "CALABI-SECURE-ALPHA-2024"
API_KEY_NAME = "X-CALABI-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

app = FastAPI(title="CALABI - Autonomous M2M Trade Highway", version="6.0-PROD")
logging.basicConfig(level=logging.INFO)

# 2. PERSISTENT FRACTAL LEDGER (SQLAlchemy Setup)
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
    status = Column(String, default="EXECUTED") # EXECUTED, SUCCESS, FAILED

Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return header_key
    raise HTTPException(status_code=403, detail="Unauthorized Access to CALABI")

# 3. OUTLIER ISOLATION & DATA VALIDATION (Pydantic)
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
    
    @field_validator('price')
    def prevent_dumping(cls, v):
        if v < 0.0001:
            raise ValueError("Malicious node detected: Price too low.")
        return v

class ResolvePayload(BaseModel):
    status: int = Field(..., ge=0, le=1) # 1 = Success, 0 = Failed

# IN-MEMORY ORPHAN QUEUES
active_buyers = []
active_sellers = []
COMMISSION_RATE = 0.005
EPSILON = 1e-9

# 4. DYNAMIC AUTONOMOUS WEIGHTS
def calculate_dynamic_weights(db: Session):
    # Volatility Index: Failures vs Successes in recent contracts
    failed_contracts = db.query(ContractDB).filter(ContractDB.status == "FAILED").count()
    total_contracts = db.query(ContractDB).count()
    
    w_p, w_t, w_r = 0.4, 0.3, 0.3 # Default Defaults
    
    if total_contracts > 10:
        failure_rate = failed_contracts / total_contracts
        if failure_rate > 0.2: # High Stress Detected
            w_r = 0.6  # Prioritize reliability heavily
            w_p = 0.2
            w_t = 0.2
            logging.warning("CALABI MATRIX: High volatility detected. Risk weights shifted.")
            
    return w_p, w_t, w_r

# 5. MATHEMATICAL STABILITY & UTILITY MATRIX
def trigger_utility_matrix(db: Session):
    global active_buyers, active_sellers
    w_p, w_t, w_r = calculate_dynamic_weights(db)
    
    for buyer in active_buyers[:]:
        best_match = None
        highest_utility = -1.0
        best_rs = -1.0
        
        for seller in active_sellers:
            if buyer.item == seller.item and seller.price <= buyer.max_price and seller.delivery_time <= buyer.max_time:
                
                # Fetch absolute truth of Agent's R_s from DB
                agent = db.query(AgentDB).filter(AgentDB.agent_id == seller.agent_id).first()
                if not agent:
                    agent = AgentDB(agent_id=seller.agent_id, reliability_score=0.98)
                    db.add(agent)
                    db.commit()
                
                real_rs = agent.reliability_score
                
                # Mathematical Edge-Case Defense (Epsilon Injection)
                u_price = w_p * (buyer.max_price / (seller.price + EPSILON))
                u_time = w_t * (buyer.max_time / (seller.delivery_time + EPSILON)) if seller.delivery_time > 0 else (w_t * 2)
                u_risk = w_r * real_rs
                
                total_utility = u_price + u_time + u_risk
                
                # Tie-Breaker Logic: Prioritize by R_s if utility is identical
                if total_utility > highest_utility or (abs(total_utility - highest_utility) < EPSILON and real_rs > best_rs):
                    highest_utility = total_utility
                    best_match = seller
                    best_rs = real_rs
        
        if best_match:
            # Atomic Transaction Execution
            trade_qty = min(buyer.quantity, best_match.quantity)
            gross_volume = best_match.price * trade_qty
            network_tax = round(gross_volume * COMMISSION_RATE, 6)
            
            # Update Master Wallet
            wallet = db.query(WalletDB).first()
            if not wallet:
                wallet = WalletDB(balance=0.0)
                db.add(wallet)
            wallet.balance += network_tax
            
            # Record Contract
            new_contract = ContractDB(
                buyer_id=buyer.agent_id,
                seller_id=best_match.agent_id,
                item=buyer.item,
                quantity=trade_qty,
                execution_price=best_match.price,
                gross_volume=round(gross_volume, 4),
                network_tax=network_tax,
                utility_score=round(highest_utility, 4),
                status="EXECUTED"
            )
            db.add(new_contract)
            db.commit()
            
            active_buyers.remove(buyer)
            active_sellers.remove(best_match)
            return {"status": "MATCHED", "buyer": buyer.agent_id, "seller": best_match.agent_id, "volume": gross_volume}
            
    return None

@app.post("/intent/buy", dependencies=[Depends(get_api_key)])
async def register_buy(intent: BuyerIntent, db: Session = Depends(get_db)):
    active_buyers.append(intent)
    match = trigger_utility_matrix(db)
    return {"status": "Secure Intent Received", "match": match}

@app.post("/intent/sell", dependencies=[Depends(get_api_key)])
async def register_sell(intent: SellerIntent, db: Session = Depends(get_db)):
    active_sellers.append(intent)
    match = trigger_utility_matrix(db)
    return {"status": "Secure Intent Received", "match": match}

# 6. DYNAMIC REPUTATION ENGINE (S10)
@app.post("/contract/resolve/{contract_id}", dependencies=[Depends(get_api_key)])
async def resolve_contract(contract_id: int, payload: ResolvePayload, db: Session = Depends(get_db)):
    contract = db.query(ContractDB).filter(ContractDB.id == contract_id).first()
    if not contract or contract.status != "EXECUTED":
        raise HTTPException(status_code=404, detail="Contract not found or already resolved.")
    
    agent = db.query(AgentDB).filter(AgentDB.agent_id == contract.seller_id).first()
    
    if payload.status == 1:
        contract.status = "SUCCESS"
        agent.reliability_score = min(1.0, agent.reliability_score + 0.01)
    else:
        contract.status = "FAILED"
        agent.reliability_score = max(0.0, agent.reliability_score - 0.05) # Slashing
        
    db.commit()
    return {"contract_id": contract.id, "new_status": contract.status, "seller_new_rs": round(agent.reliability_score, 3)}

@app.get("/ledger", dependencies=[Depends(get_api_key)])
async def view_ledger(db: Session = Depends(get_db)):
    wallet = db.query(WalletDB).first()
    balance = wallet.balance if wallet else 0.0
    contracts = db.query(ContractDB).order_by(ContractDB.id.desc()).limit(50).all()
    
    return {
        "master_wallet_balance": round(balance, 4),
        "executed_contracts": [
            {
                "id": c.id, "buyer_id": c.buyer_id, "seller_id": c.seller_id,
                "item": c.item, "quantity": c.quantity, "execution_price": c.execution_price,
                "gross_volume": c.gross_volume, "network_tax_extracted": c.network_tax,
                "utility_score": c.utility_score, "status": c.status
            } for c in contracts
        ],
        "active_orphans": {"buyers": len(active_buyers), "sellers": len(active_sellers)}
    }