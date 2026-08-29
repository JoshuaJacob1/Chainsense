import os
import json
import asyncio
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import duckdb

app = FastAPI(title="ChainSense API")

# Allow CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # TODO: restrict to vercel URL in prod
    allow_methods=["GET"],
)

# Connect to our local duckdb file where features and labels will be saved
DB_PATH = os.path.join(os.path.dirname(__file__), "../data/chainsense.db")
con = duckdb.connect(DB_PATH)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "ChainSense API is running"}

@app.get("/api/wallet/{address}")
def get_wallet(address: str):
    """
    Look up a wallet's behavioral features and assigned cluster.
    """
    address = address.lower()
    
    try:
        feat_query = f"SELECT * FROM wallet_features WHERE address = '{address}'"
        label_query = f"SELECT * FROM wallet_labels WHERE address = '{address}'"
        
        feats = con.execute(feat_query).df().to_dict(orient="records")
        labels = con.execute(label_query).df().to_dict(orient="records")
        
        if not feats:
            return {"found": False, "address": address}
            
        return {
            "found": True,
            "address": address,
            "cluster": labels[0]["cluster"] if labels else -1,
            "features": feats[0]
        }
    except Exception as e:
        # DB might not be initialized yet
        return {"error": str(e), "found": False}

@app.get("/api/stream")
async def get_stream():
    """
    Live Server-Sent Events (SSE) feed for the dashboard.
    In production, this drains the live queue classified by XGBoost.
    """
    async def event_generator():
        yield f"data: {json.dumps({'type': 'connected', 'message': 'Stream active'})}\n\n"
        
        families = ["Retail Dex Trader", "Phishing / Drainer", "NFT Flipper", "DeFi Whale", "Bot / MEV"]
        
        # Simulate the live block ingestion for now
        while True:
            await asyncio.sleep(random.randint(2, 6))
            mock_addr = "0x" + "".join(random.choices("0123456789abcdef", k=40))
            
            ev = {
                "type": "classification",
                "data": {
                    "addr": mock_addr,
                    "family": random.choice(families),
                    "conf": round(random.uniform(0.65, 0.99), 2),
                    "time": "Just now"
                }
            }
            yield f"data: {json.dumps(ev)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
