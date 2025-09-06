from fastapi import FastAPI, Query
from datetime import datetime

app = FastAPI()

@app.post("/traccar")
@app.get("/traccar")  # Traccar can use GET or POST
async def receive_location(
    deviceid: str = Query(...),   # Traccar sends "deviceid"
    lat: float = Query(...),      # Traccar sends "lat"
    lon: float = Query(...),      # Traccar sends "lon"
    speed: float = Query(0)
):
    data = {
        "device_id": deviceid,
        "latitude": lat,
        "longitude": lon,
        "speed": speed,
        "received_at": datetime.utcnow().isoformat()
    }

    print("Received:", data)
    return {"status": "ok", "data": data}
