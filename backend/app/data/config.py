from . import PermanentModel


class EnergyConfig(PermanentModel):
    _path = "/data/energy_config"

    site_id: int
    site_name: str


class VehicleConfig(PermanentModel):
    _path = "/data/vehicle_config"

    id: int
    vehicle_id: int
    display_name: str
