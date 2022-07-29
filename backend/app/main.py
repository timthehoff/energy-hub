from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import auth, energy, vehicle

app = FastAPI()
app.include_router(auth.router)
app.include_router(energy.router)
app.include_router(vehicle.router)


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")
