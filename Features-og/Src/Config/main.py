import sys
import os

# Agregar la carpeta Src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from Config.database import Base, engine
from Routes.auth import router as auth_router

# Crear tablas en la BD
Base.metadata.create_all(bind=engine)

# Inicializar FastAPI
app = FastAPI(
    title="Lynko API",
    description="API para la plataforma educativa Lynko",
    version="1.0.0"
)

# CORS - Permitir requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos (HTML, CSS, JS)
pages_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../Pages"))

try:
    app.mount("/static", StaticFiles(directory=pages_dir), name="static")
    print(f"✅ Sirviendo archivos desde: {pages_dir}")
except Exception as e:
    print(f"⚠️ Advertencia: No se pudo montar carpeta Pages: {e}")

# Registrar routers
app.include_router(auth_router)

@app.get("/")
def read_root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a Lynko API",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /api/auth/register",
            "login": "POST /api/auth/login",
            "me": "GET /api/auth/me"
        }
    }

@app.get("/health")
def health_check():
    """Health check"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)