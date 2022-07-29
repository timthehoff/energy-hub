from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from teslapy import Tesla

from app import get_tesla
from app.data.config import VehicleConfig

router = APIRouter(prefix="/vehicles")


async def get_config() -> VehicleConfig:
    try:
        return VehicleConfig.load()
    except FileNotFoundError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="Vehicle not configured"
        )


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
