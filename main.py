from fastapi import FastAPI, Form
from datetime import datetime

app = FastAPI()

@app.post("/traccar")
async def receive_location(
    device_id: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    speed: float = Form(0)
):
    # For now just print and return the data
    data = {
        "device_id": device_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed": speed,
        "received_at": datetime.utcnow().isoformat()
    }

    print("Received:", data)

    return {"status": "ok", "data": data}
