from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.procesos.inventario import router as inventario_router
from app.procesos.agendamiento_v2 import router as agendamiento_v2_router
from app.procesos.liquidacion import router as liquidacion_router


app = FastAPI(root_path="/agendamientos")

# 🔹 Crear app
app = FastAPI(title="Portal de Procesos Mexicargo")

# 🔹 Templates y static
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 🔹 Routers
app.include_router(inventario_router)
app.include_router(agendamiento_v2_router)
app.include_router(liquidacion_router)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
