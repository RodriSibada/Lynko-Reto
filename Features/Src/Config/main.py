from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🔹 conexión DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios")
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    nuevo = models.Usuario(**usuario.dict(), puntaje=0)
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.get("/usuarios")
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@app.get("/usuarios/{id}")
def obtener_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return usuario

@app.put("/usuarios/{id}")
def actualizar_usuario(id: int, datos: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.nombre = datos.nombre
    usuario.correo = datos.correo
    usuario.contraseña = datos.contraseña

    db.commit()
    return usuario

@app.delete("/usuarios/{id}")
def eliminar_usuario(id: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.delete(usuario)
    db.commit()

    return {"mensaje": "Usuario eliminado"}
