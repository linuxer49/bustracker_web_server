from fastapi import FastAPI, Request
from datetime import datetime

app = FastAPI()

@app.post("/traccar")
async def receive_location(request: Request):
    raw_body = await request.body()
    headers = dict(request.headers)

    print("=== RAW REQUEST BODY ===")
    print(raw_body.decode("utf-8"))
    print("=== HEADERS ===")
    print(headers)

    return {
        "status": "received",
        "raw_body": raw_body.decode("utf-8"),
        "headers": headers,
        "received_at": datetime.utcnow().isoformat()
    }
