from asyncio import sleep
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from teslapy import Tesla

from app import get_tesla
from app.data.config import VehicleConfig

WAKE_SLEEP = 2
WAKE_TIMEOUT = 60

router = APIRouter(prefix="/vehicles")


async def get_config() -> VehicleConfig:
    try:
        return VehicleConfig.load()
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Vehicle not configured"
        )


async def is_awake(tesla: Tesla, vehicle_id: int) -> bool:
    response = tesla.api("VEHICLE_SUMMARY", path_vars={"vehicle_id": vehicle_id})
    return response["response"]["state"] == "online"


async def wake_and_run(
    tesla: Tesla, vehicle_id: int, command: str, params: dict = None
) -> dict:

    # Wake up.
    for _ in range(WAKE_TIMEOUT // WAKE_SLEEP):
        if await is_awake(tesla, vehicle_id):
            break

        tesla.api("WAKE_UP", path_vars={"vehicle_id": vehicle_id})
        await sleep(2)

    else:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Unable to wake vehicle",
        )

    # Run command.
    params = params or {}
    response: dict = tesla.api(command, path_vars={"vehicle_id": vehicle_id}, **params)
    return response.get("response") or response


@router.get("", tags=["Vehicles"])
async def list_vehicles(tesla: Tesla = Depends(get_tesla)) -> Dict[int, str]:
    vehicles = tesla.vehicle_list()
    return {vehicle["id"]: vehicle["display_name"] for vehicle in vehicles}


@router.post("/config", tags=["Vehicles"])
async def configure(vehicle_id: int, tesla: Tesla = Depends(get_tesla)):
    vehicles = tesla.vehicle_list()
    for vehicle in vehicles:
        if vehicle["id"] == vehicle_id:
            break
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle {vehicle_id} not found",
        )

    config = VehicleConfig(
        id=vehicle["id"],
        vehicle_id=vehicle["vehicle_id"],
        display_name=vehicle["display_name"],
    )
    config.save()


@router.get("/status", tags=["Vehicles"])
async def get_status(
    tesla: Tesla = Depends(get_tesla), config: VehicleConfig = Depends(get_config)
) -> dict:
    response: dict = tesla.api("VEHICLE_DATA", path_vars={"vehicle_id": config.id})
    return response["response"]


@router.post("/charge/start", tags=["Vehicles", "Charging"])
async def start_charging(
    tesla: Tesla = Depends(get_tesla), config: VehicleConfig = Depends(get_config)
):
    return await wake_and_run(tesla, config.id, "START_CHARGE")


@router.post("/charge/stop", tags=["Vehicles", "Charging"])
async def stop_charging(
    tesla: Tesla = Depends(get_tesla), config: VehicleConfig = Depends(get_config)
):
    return await wake_and_run(tesla, config.id, "STOP_CHARGE")


@router.post("/charge/limit", tags=["Vehicles", "Charging"])
async def set_charge_limit(
    percent: int,
    tesla: Tesla = Depends(get_tesla),
    config: VehicleConfig = Depends(get_config),
):
    return await wake_and_run(
        tesla, config.id, "CHANGE_CHARGE_LIMIT", params={"percent": percent}
    )


@router.post("/charge/amps", tags=["Vehicles", "Charging"])
async def set_charge_amps(
    amps: int,
    tesla: Tesla = Depends(get_tesla),
    config: VehicleConfig = Depends(get_config),
):
    return await wake_and_run(
        tesla, config.id, "CHARGING_AMPS", params={"charging_amps": amps}
    )
