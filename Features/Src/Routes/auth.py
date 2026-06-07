"""
RUTAS DE AUTENTICACIÓN - auth.py

Define los endpoints HTTP:
- POST /api/auth/registro - Registrar nuevo usuario
- POST /api/auth/login - Iniciar sesión
- GET /api/auth/me - Obtener datos del usuario logueado
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..Config.database import SessionLocal
from ..Controllers.auth_controller import (
    registrar_usuario,
    login_usuario,
    verificar_token,
    obtener_usuario_por_id
)
from ..Config.schemas import UsuarioCreate

# Crear router para agrupar las rutas de autenticación
router = APIRouter(
    prefix="/api/auth",
    tags=["autenticacion"]
)

#Schemas

class LoginRequest(BaseModel):
    """Esquema para solicitud de login"""
    correo: str
    contraseña: str


class RegistroRequest(BaseModel):
    """Esquema para solicitud de registro"""
    nombre: str
    correo: str
    contraseña: str



def get_db():
    """
    Dependencia que proporciona una sesión de BD para cada request
    
    FastAPI ejecuta esto automáticamente y lo inyecta en los endpoints
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/registro")
async def endpoint_registro(
    datos: RegistroRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para registrar un nuevo usuario
    
    Request:
    {
        "nombre": "Juan Pérez",
        "correo": "juan@example.com",
        "contraseña": "Segura123"
    }
    
    Response (Éxito):
    {
        "success": true,
        "mensaje": "Usuario registrado exitosamente",
        "id_usuario": 1,
        "usuario": {
            "id_usuario": 1,
            "nombre": "Juan Pérez",
            "correo": "juan@example.com",
            "puntaje": 0
        }
    }
    
    Response (Error):
    {
        "success": false,
        "error": "El correo electrónico ya está registrado"
    }
    """
    
    print(f"📝 Solicitud de REGISTRO: {datos.correo}")
    
    # Validaciones básicas en servidor (adicional a las del cliente)
    if len(datos.nombre) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre debe tener mínimo 3 caracteres"
        )
    
    if len(datos.contraseña) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener mínimo 8 caracteres"
        )
    
    # Llamar al controlador
    usuario_create = UsuarioCreate(
        nombre=datos.nombre,
        correo=datos.correo,
        contraseña=datos.contraseña
    )
    
    resultado = registrar_usuario(usuario_create, db)
    
    # Retornar resultado
    return resultado


@router.post("/login")
async def endpoint_login(
    datos: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para iniciar sesión
    
    Request:
    {
        "correo": "juan@example.com",
        "contraseña": "Segura123"
    }
    
    Response (Éxito):
    {
        "success": true,
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "token_type": "bearer",
        "usuario": {
            "id_usuario": 1,
            "nombre": "Juan Pérez",
            "correo": "juan@example.com",
            "puntaje": 0
        }
    }
    
    Response (Error):
    {
        "success": false,
        "error": "Correo o contraseña incorrectos"
    }
    """
    
    print(f"🔐 Solicitud de LOGIN: {datos.correo}")
    
    # Validaciones básicas
    if not datos.correo or not datos.contraseña:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email y contraseña son requeridos"
        )
    
    # Llamar al controlador
    resultado = login_usuario(datos.correo, datos.contraseña, db)
    
    # Retornar resultado
    return resultado


# =====================================================
# ENDPOINT 3: OBTENER USUARIO ACTUAL
# =====================================================

@router.get("/me")
async def endpoint_obtener_usuario_actual(
    token: str = None,  # En un caso real, esto vendría del header Authorization
    db: Session = Depends(get_db)
):
    """
    Endpoint para obtener datos del usuario logueado
    
    Requiere token válido
    
    Response:
    {
        "id_usuario": 1,
        "nombre": "Juan Pérez",
        "correo": "juan@example.com",
        "puntaje": 0,
        "fecha_registro": "2024-01-15T10:30:00"
    }
    """
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado"
        )
    
    # Verificar token
    usuario_id = verificar_token(token)
    
    if usuario_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )
    
    # Obtener datos del usuario
    usuario = obtener_usuario_por_id(usuario_id, db)
    
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return usuario



# HEALTH CHECK (para verificar que el servidor funciona)

@router.get("/health")
async def health_check():
    """
    Endpoint para verificar que el servidor está funcionando
    
    Response: { "status": "ok" }
    """
    return {"status": "ok", "mensaje": "🟢 Servidor Lynko funcionando"}
