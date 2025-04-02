from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Global flag to simulate failure
failure_mode = False

# Endpoints for S3 and RDS, injected via environment variables
PRIMARY_S3_URL = os.getenv("PRIMARY_S3_URL", "https://primary.s3.example.com")
PRIMARY_RDS_ENDPOINT = os.getenv("PRIMARY_RDS_ENDPOINT", "primary-db.example.com")
DR_S3_URL = os.getenv("DR_S3_URL", "https://dr.s3.example.com")
DR_RDS_ENDPOINT = os.getenv("DR_RDS_ENDPOINT", "dr-db.example.com")

USE_DR = os.getenv("USE_DR", "false").lower() == "true"

@app.middleware("http")
async def failure_simulation_middleware(request: Request, call_next):
    global failure_mode
    if failure_mode:
        # Simulate a failure response
        return JSONResponse(status_code=500, content={"detail": "Simulated failure"})
    response = await call_next(request)
    return response

@app.get("")
async def root():
    return {"message": "Welcome to the API!"}

@app.get("/status")
async def status():
    # Return current endpoints depending on whether DR is active
    if USE_DR:
        return {"S3_URL": DR_S3_URL, "RDS_ENDPOINT": DR_RDS_ENDPOINT, "mode": "DR"}
    else:
        return {"S3_URL": PRIMARY_S3_URL, "RDS_ENDPOINT": PRIMARY_RDS_ENDPOINT, "mode": "Primary"}

@app.post("/simulate_failure")
async def simulate_failure(activate: bool):
    global failure_mode
    failure_mode = activate
    return {"failure_mode": failure_mode}
