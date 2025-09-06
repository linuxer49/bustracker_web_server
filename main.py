from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

app = FastAPI()

@app.post("/traccar")
async def receive_traccar(request: Request):
    try:
        content_type = request.headers.get("content-type", "")

        data = {}
        if "application/json" in content_type:
            body = await request.json()
            location = body.get("location", {})
            coords = location.get("coords", {})

            data = {
                "device_id": body.get("device_id"),
                "latitude": coords.get("latitude"),
                "longitude": coords.get("longitude"),
                "speed": coords.get("speed"),
                "altitude": coords.get("altitude"),
                "accuracy": coords.get("accuracy"),
                "event": location.get("event"),
                "timestamp": location.get("timestamp", datetime.utcnow().isoformat())
            }

        elif "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            data = dict(form)

        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported content type"})

        # 🟢 Insert into Supabase
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{SUPABASE_URL}/rest/v1/bus_locations",
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "device_id": data["device_id"],
                    "latitude": data["latitude"],
                    "longitude": data["longitude"],
                    "speed": data["speed"],
                    "recorded_at": data["timestamp"]
                }
            )

        if resp.status_code not in [200, 201]:
            return JSONResponse(
                status_code=resp.status_code,
                content={"error": "Supabase insert failed", "details": resp.text}
            )

        print("📍 Location stored:", data)
        return {"status": "ok", "data": data}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
