from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app import auth, energy

app = FastAPI()
app.include_router(auth.router)
app.include_router(energy.router)


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")
