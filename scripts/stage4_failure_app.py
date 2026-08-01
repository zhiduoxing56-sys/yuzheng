from app.main import app
from app.services.vehicle.simulator import SimulatorVehicleAdapter


class AcceptanceFailingAdapter(SimulatorVehicleAdapter):
    adapter_name = "failing_simulator"

    def execute(self, action: str, target: str, area: str):
        del action, target, area
        raise RuntimeError("阶段四验收受控适配器失败")


pipeline = app.state.pipeline
pipeline.vehicle = AcceptanceFailingAdapter(
    initial_state=pipeline.vehicle.get_state(),
    action_config=pipeline.vehicle_config,
)
