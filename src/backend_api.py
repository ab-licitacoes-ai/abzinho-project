import os
from fastapi import FastAPI, Request
from .routers import auth, task 

# Import environment variables
from .config.database import get_db_connection, N8N_WEBHOOK_URL

API_PREFIX = "/api/v1"
app = FastAPI(title="ABzinho API de Gestão", version="1.0", openapi_prefix=API_PREFIX)

# Middleware to handle CORS
@app.middleware("http")
async def secure_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# Incluir o router de autenticação: Caminho final: /api/v1/auth/...
app.include_router(auth.router, prefix=API_PREFIX)

# Incluir o router de tarefas: Caminho final: /api/v1/tasks/...
app.include_router(task.router, prefix=API_PREFIX)