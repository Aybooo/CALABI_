from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from starlette.status import HTTP_403_FORBIDDEN

app = FastAPI(title="CALABI - Secure Apex Grid", version="5.5")

# SECURITY PROTOCOL
API_KEY = "CALABI-SECURE-ALPHA-2024"
API_KEY_NAME = "X-CALABI-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(header_key: str = Security(api_key_header)):
    if header_key == API_KEY:
        return header_key
    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Unauthorized Access to CALABI")

# STATE & LEDGER
buy_intents = []
sell_intents = []
executed_contracts = []
system_wallet_balance = 0.0
COMMISSION_RATE = 0.005

class BuyerIntent(BaseModel):
    agent_id: str
    item: str
    quantity: int
    max_price: float
    max_time: int
    weight_price: float
    weight_time: float
    weight_risk: float

class SellerIntent(BaseModel):
    agent_id: str
    item: str
    quantity: int
    price: float
    delivery_time: int
    reliability_score: float

def trigger_utility_matrix():
    global buy_intents, sell_intents, executed_contracts, system_wallet_balance
    for buyer in buy_intents[:]:
        best_match = None
        highest_utility = 0.0
        for seller in sell_intents:
            if buyer.item == seller.item and seller.price <= buyer.max_price and seller.delivery_time <= buyer.max_time:
                u_price = buyer.weight_price * (buyer.max_price / seller.price)
                u_time = buyer.weight_time * (buyer.max_time / seller.delivery_time) if seller.delivery_time > 0 else buyer.weight_time * 2
                u_risk = buyer.weight_risk * seller.reliability_score
                total_utility = u_price + u_time + u_risk
                
                if total_utility > highest_utility:
                    highest_utility = total_utility
                    best_match = seller
        
        if best_match:
            trade_qty = min(buyer.quantity, best_match.quantity)
            gross_volume = best_match.price * trade_qty
            network_tax = round(gross_volume * COMMISSION_RATE, 4)
            seller_net = round(gross_volume - network_tax, 4)
            
            system_wallet_balance += network_tax
            contract = {
                "buyer_id": buyer.agent_id,
                "seller_id": best_match.agent_id,
                "item": buyer.item,
                "quantity": trade_qty,
                "execution_price": best_match.price,
                "gross_volume": round(gross_volume, 2),
                "network_tax_extracted": network_tax,
                "seller_net_payout": seller_net,
                "utility_score": round(highest_utility, 3),
                "status": "APEX_CONTRACT_EXECUTED"
            }
            executed_contracts.append(contract)
            buy_intents.remove(buyer)
            sell_intents.remove(best_match)
            return contract
    return None

@app.post("/intent/buy", dependencies=[Depends(get_api_key)])
async def register_buy(intent: BuyerIntent):
    buy_intents.append(intent)
    match = trigger_utility_matrix()
    return {"status": "Secure Intent Received", "match": match}

@app.post("/intent/sell", dependencies=[Depends(get_api_key)])
async def register_sell(intent: SellerIntent):
    sell_intents.append(intent)
    match = trigger_utility_matrix()
    return {"status": "Secure Intent Received", "match": match}

@app.get("/ledger", dependencies=[Depends(get_api_key)])
async def view_ledger():
    return {
        "master_wallet_balance": round(system_wallet_balance, 4),
        "active_buy_intents": buy_intents, 
        "active_sell_intents": sell_intents, 
        "executed_contracts": executed_contracts
    }