from . import PermanentModel


class EnergyConfig(PermanentModel):
    _path = "/data/energy_config"

    site_id: int
    site_name: str
