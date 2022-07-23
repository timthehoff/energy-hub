from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from teslapy import Tesla

from app import get_tesla

router = APIRouter(prefix="/energy")


@router.get("/status", tags=["Energy"])
async def get_status(tesla: Tesla = Depends(get_tesla)):
    batteries = tesla.battery_list()
    if not batteries:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No batteries in account"
        )
    return tesla.api("SITE_DATA", path_vars={"site_id": batteries[0]["energy_site_id"]})
