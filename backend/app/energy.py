from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from teslapy import Tesla

from app import get_tesla
from app.data.config import EnergyConfig

router = APIRouter(prefix="/energy")


async def get_config() -> EnergyConfig:
    try:
        return EnergyConfig.load()
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Energy site not configured"
        )


@router.get("", tags=["Energy"])
async def list_sites(tesla: Tesla = Depends(get_tesla)) -> Dict[int, str]:
    sites = tesla.battery_list()
    return {site["energy_site_id"]: site["site_name"] for site in sites}


@router.post("/config", tags=["Energy"])
async def configure(site_id: int, tesla: Tesla = Depends(get_tesla)):
    sites = await list_sites(tesla)
    if site_id not in sites:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Site {site_id} not found"
        )

    config = EnergyConfig(site_id=site_id, site_name=sites[site_id])
    config.save()


@router.get("/status", tags=["Energy"])
async def get_status(
    tesla: Tesla = Depends(get_tesla), config: EnergyConfig = Depends(get_config)
) -> dict:
    response: dict = tesla.api("SITE_DATA", path_vars={"site_id": config.site_id})
    return response["response"]


@router.get("/soc", tags=["Energy"])
async def get_soc(
    tesla: Tesla = Depends(get_tesla), config: EnergyConfig = Depends(get_config)
) -> int:
    status = await get_status(tesla, config)
    return round(status["percentage_charged"])


@router.get("/excess-solar", tags=["Energy"])
async def get_excess_solar(
    tesla: Tesla = Depends(get_tesla), config: EnergyConfig = Depends(get_config)
) -> int:
    status = await get_status(tesla, config)
    charging = -min(status["battery_power"], 0)
    return max(status["solar_power"] - status["load_power"] - charging, 0)


@router.get("/charging-for-event", tags=["Energy"])
async def get_charging_for_event(
    tesla: Tesla = Depends(get_tesla), config: EnergyConfig = Depends(get_config)
) -> bool:
    status = await get_status(tesla, config)
    return status["grid_power"] > 0 and status["battery_power"] < 0
