rom fastapi import FastAPI, Form
from datetime import datetime

app = FastAPI()

@app.post("/traccar")
async def receive_location(
    id: str = Form(...),       # Traccar sends "id" (device identifier)
    lat: float = Form(...),    # Traccar sends "lat"
    lon: float = Form(...),    # Traccar sends "lon"
    speed: float = Form(0)     # Optional
):
    data = {
        "device_id": id,
        "latitude": lat,
        "longitude": lon,
        "speed": speed,
        "received_at": datetime.utcnow().isoformat()
    }

    print("Received:", data)
    return {"status": "ok", "data": data}
