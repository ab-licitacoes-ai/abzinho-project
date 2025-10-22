import os
from fastapi import APIRouter, HTTPException, Body
from typing import Dict

from ..config.database import N8N_WEBHOOK_URL

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)

# Authentication endpoint
@router.post("/login")
def login_user(email: str = Body(..., embed=True), password: str = Body(..., embed=True)) -> Dict[str, str]:
    if email and password:
        secret = os.getenv("SECRET_KEY", "fallback_secret_key")
        return {"access_token": f"jwt_token_for_{email}_{secret[:10]}", "token_type": "bearer"}
    raise HTTPException(status_code=400, detail="Credenciais inválidas")


                