from fastapi import FastAPI, Form, HTTPException
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI()

@app.post("/traccar")
async def receive_location(
    device_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    speed: float = Form(0)
):
    # 1️⃣ Validate inputs
    if not device_id:
        raise HTTPException(status_code=400, detail="Missing device_id")
    if latitude is None or longitude is None:
        raise HTTPException(status_code=400, detail="Missing latitude or longitude")

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 2️⃣ Find bus by device_id
            bus_resp = await client.get(
                f"{SUPABASE_URL}/rest/v1/buses",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                },
                params={"device_id": f"eq.{device_id}"}
            )

            if bus_resp.status_code != 200:
                raise HTTPException(
                    status_code=bus_resp.status_code,
                    detail=f"Failed to fetch bus info: {bus_resp.text}"
                )

            buses = bus_resp.json()
            if not buses:
                raise HTTPException(status_code=404, detail=f"No bus found for device_id {device_id}")

            bus_id = buses[0]["id"]

            # 3️⃣ Insert location into Supabase
            resp = await client.post(
                f"{SUPABASE_URL}/rest/v1/bus_locations",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "bus_id": bus_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "speed": speed,
                    "recorded_at": datetime.utcnow().isoformat()
                }
            )

            if resp.status_code not in [200, 201]:
                raise HTTPException(
                    status_code=resp.status_code,
                    detail=f"Failed to insert location: {resp.text}"
                )

    except httpx.RequestError as e:
        # Network or timeout issues
        raise HTTPException(status_code=503, detail=f"HTTP request error: {str(e)}")
    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=f"Unexpected server error: {str(e)}")

    # 4️⃣ Success
    return {"status": "ok", "bus_id": bus_id, "device_id": device_id}
