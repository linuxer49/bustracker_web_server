from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI()

@app.post("/traccar")
async def receive_location(request: Request):
    data = await request.json()

    # Extract values from Traccar / dummy input
    bus_id = data.get("bus_id")  # Later: map IMEI → bus_id
    lat = data.get("latitude")
    lon = data.get("longitude")
    speed = data.get("speed", 0)

    if not (bus_id and lat and lon):
        return {"error": "Missing required fields"}

    # Insert into Supabase REST API
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/bus_locations",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "bus_id": bus_id,
                "latitude": lat,
                "longitude": lon,
                "speed": speed,
                "recorded_at": datetime.utcnow().isoformat()
            }
        )

    if resp.status_code not in [200, 201]:
        return {"error": "Supabase insert failed", "details": resp.text}

    return {"status": "ok", "bus_id": bus_id}
