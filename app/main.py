from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from pathlib import Path

app = FastAPI(title="Coin Compass API")

# ----------------------------------
#       Local Development
# ----------------------------------
from dotenv import load_dotenv

load_dotenv()
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "static"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


# ----------------------------------


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    user_id: str
    password: str


@app.post("/api/login")
def login(credentials: LoginRequest):
    # Uses Render environment variables if set, otherwise defaults for local testing
    correct_user = os.getenv("USER_ID")
    correct_pass = os.getenv("PASSWORD")

    if not correct_pass or not correct_user:
        raise HTTPException(status_code=500, detail="Environment not set properly")

    if credentials.user_id == correct_user and credentials.password == correct_pass:
        # A dummy token for this project. In a production app, use a real JWT.
        return {"token": "coin-compass-secret-token-xyz"}

    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/summary")
def get_financial_summary(authorization: str = Header(None)):
    expected_token = "Bearer coin-compass-secret-token-xyz"

    # Block anyone trying to hit this endpoint without the correct token
    if not authorization or authorization != expected_token:
        raise HTTPException(status_code=401, detail="Unauthorized access")

    # Serve the data if the token is valid
    return {"total_balance": 24500, "monthly_expenses": 8200, "currency": "₹"}
