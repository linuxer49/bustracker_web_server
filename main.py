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

    # Extract IMEI/uniqueId from Traccar
    imei = data.get("uniqueId") or data.get("imei") \
           or (data.get("attributes", {}).get("uniqueId"))
    lat = data.get("latitude")
    lon = data.get("longitude")
    speed = data.get("speed", 0)

    if not (imei and lat and lon):
        return {"error": "Missing required fields", "received": data}

    async with httpx.AsyncClient() as client:
        # 1) Find bus by IMEI
        bus_resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/buses",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
            },
            params={"imei": f"eq.{imei}"}
        )

        if bus_resp.status_code != 200 or not bus_resp.json():
            return {"error": "Bus not found for IMEI", "imei": imei}

        bus_id = bus_resp.json()[0]["id"]

        # 2) Insert into bus_locations
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

    return {"status": "ok", "bus_id": bus_id, "imei": imei}
