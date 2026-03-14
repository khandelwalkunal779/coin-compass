from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import jwt
import datetime

if os.getenv("ENVIRONMENT") != "prod":
    from dotenv import load_dotenv

    load_dotenv()

app = FastAPI(title="Coin Compass API")


@app.get("/")
def root():
    return FileResponse("static/index.html")


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


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    return secret


@app.post("/api/login")
def login(credentials: LoginRequest):
    correct_user = os.getenv("USER_ID")
    correct_pass = os.getenv("PASSWORD")

    if not correct_user or not correct_pass:
        raise HTTPException(status_code=500, detail="Environment not set properly")

    if credentials.user_id != correct_user or credentials.password != correct_pass:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": credentials.user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    token = jwt.encode(payload, _jwt_secret(), algorithm="HS256")
    return {"token": token}


@app.get("/api/summary")
def get_financial_summary(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized access")

    token = authorization.removeprefix("Bearer ")
    try:
        jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"total_balance": 24500, "monthly_expenses": 8200, "currency": "₹"}
