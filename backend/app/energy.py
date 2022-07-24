from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from teslapy import Tesla

from app import get_tesla

router = APIRouter(prefix="/energy")


@router.get("/status", tags=["Energy"])
async def get_status(tesla: Tesla = Depends(get_tesla)) -> dict:
    batteries = tesla.battery_list()
    if not batteries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No batteries in account"
        )
    response: dict = tesla.api(
        "SITE_DATA", path_vars={"site_id": batteries[0]["energy_site_id"]}
    )
    return response["response"]


@router.get("/soc", tags=["Energy"])
async def get_soc(tesla: Tesla = Depends(get_tesla)) -> int:
    status = await get_status(tesla)
    return round(status["percentage_charged"])


@router.get("/excess-solar", tags=["Energy"])
async def get_excess_solar(tesla: Tesla = Depends(get_tesla)) -> int:
    status = await get_status(tesla)
    charging = -min(status["battery_power"], 0)
    return max(status["solar_power"] - status["load_power"] - charging, 0)


@router.get("/charging-for-event", tags=["Energy"])
async def get_charging_for_event(tesla: Tesla = Depends(get_tesla)) -> bool:
    status = await get_status(tesla)
    return status["grid_power"] > 0 and status["battery_power"] < 0
