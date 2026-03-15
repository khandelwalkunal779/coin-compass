from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import jwt
import datetime

if os.getenv("ENVIRONMENT") != "prod":
    from dotenv import load_dotenv

    load_dotenv()

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")

app = FastAPI(title="Coin Compass API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return FileResponse("static/index.html")


class LoginRequest(BaseModel):
    user_id: str
    password: str


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    return secret


def _verify_cookie(request: Request) -> dict:
    token = request.cookies.get("compass_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    try:
        return jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


IS_PROD = os.getenv("ENVIRONMENT") == "prod"

COOKIE_OPTS = dict(
    key="compass_token",
    httponly=True,
    secure=IS_PROD,
    samesite="none" if IS_PROD else "strict",
    path="/",
)


@app.post("/api/login")
def login(credentials: LoginRequest, response: Response):
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
    response.set_cookie(value=token, max_age=3600, **COOKIE_OPTS)
    return {"ok": True}


@app.post("/api/logout")
def logout(response: Response):
    response.set_cookie(value="", max_age=0, **COOKIE_OPTS)
    return {"ok": True}


@app.get("/api/summary")
def get_financial_summary(request: Request):
    _verify_cookie(request)
    return {"total_balance": 24500, "monthly_expenses": 8200, "currency": "₹"}
