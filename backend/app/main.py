import teslapy
from fastapi import FastAPI, HTTPException
from starlette import status

app = FastAPI()


@app.get("/")
async def get_root():
    return {"Hello": "World"}


@app.get("/state")
async def get_state():
    with teslapy.Tesla("timandchrisct@gmail.com") as tesla:
        if not tesla.authorized:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, detail="Not logged in to Tesla account"
            )
        battery = tesla.battery_list()[0]
        return tesla.api("SITE_DATA", path_vars={"site_id": battery["energy_site_id"]})
