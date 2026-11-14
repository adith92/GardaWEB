"""Local ClearCam multipart notification forwarding proxy, with shared secret.

Run only after setting GARDA_CLEARCAM_TOKEN. Keep on loopback if ClearCam local.
Requires FastAPI, python-multipart and httpx. No image is relayed.
"""
import os
import httpx
from fastapi import FastAPI, Form, HTTPException

app = FastAPI(title="GARDA ClearCam local relay")


@app.post("/notify/{camera_id}")
async def receive(camera_id: str, text: str = Form(default=""), body_text: str = Form(default="")):
    secret = os.environ.get("GARDA_CLEARCAM_TOKEN", "")
    if len(secret) < 24:
        raise HTTPException(503, "Relay disabled: secret missing")
    # Camera ID only from predefined mapping, not user-specified URL.
    allowed = os.environ.get("GARDA_CLEARCAM_CAMERA_IDS", "LAB-CAM-01").split(",")
    if camera_id not in allowed:
        raise HTTPException(404, "Unknown camera")
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.post(f"http://127.0.0.1:8765/api/v1/clearcam/notification?camera={camera_id}",
                                    headers={"Authorization": "Bearer " + secret}, data={"text": text[:1000], "body_text": body_text[:1000]})
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8766)
