import teslapy
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from starlette import status

from .auth import router as auth_router

app = FastAPI()
app.include_router(auth_router)


@app.get("/")
async def redirect_to_docs():
    return RedirectResponse("/docs")


@app.get("/state")
async def get_state():
    with teslapy.Tesla("timandchrisct@gmail.com") as tesla:
        if not tesla.authorized:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Not logged in to Tesla account"
            )
        battery = tesla.battery_list()[0]
        return tesla.api("SITE_DATA", path_vars={"site_id": battery["energy_site_id"]})
