import smolagents

from typing import Dict, Any, Union, cast

from .fastener_toolkit import (
    get_joint_constant,
    get_tensile_stress_area,
    bolt_yield_safety_factor,
)
from .inputs import INPUTS


class AnalyticalTool(smolagents.tools.Tool):
    """
    A tool that calculates the factor of safety for a bolted connection using analytical expressions.

    This tool uses established engineering formulas to compute the factor of safety for a bolted connection
    based on the provided parameters.
    """

    name = "analytical_fos_calculation"
    description = "Calculates the factor of safety using analytical expressions."
    
    input_type = dict[str, dict[str, Union[str, type, bool]]]
    inputs: input_type = cast(input_type,INPUTS)

    output_type = "number"

    def forward(
        self,
        desired_safety_factor: float,
        load: float,
        preload: float,
        num_bolts: int,
        bolt_diameter: float,
        bolt_yield_strength: float,
        bolt_elastic_modulus: float,
        plate_thickness: float,
        plate_elastic_modulus: float,
        plate_yield_strength: float,
        pitch: float,
    ) -> str:

        load_per_bolt = load / num_bolts
        preload_per_bolt = preload / num_bolts
        tensile_area = get_tensile_stress_area(bolt_diameter, pitch)

        c = get_joint_constant(
            bolt_diameter,
            plate_thickness * 2,
            plate_elastic_modulus,
            bolt_elastic_modulus,
        )

        bolt_fos = bolt_yield_safety_factor(
            c=c,
            load=load_per_bolt,
            preload=preload_per_bolt,
            a_ts=tensile_area,
            b_ys=bolt_yield_strength,
        )

        bearing_area = bolt_diameter * plate_thickness * num_bolts
        bearing_stress = load / bearing_area
        allowable_bearing_stress = 1.5 * plate_yield_strength
        plate_fos = allowable_bearing_stress / bearing_stress

        if bolt_fos > desired_safety_factor + 0.1:
            bolt_comparison = "higher than desired"
        elif bolt_fos < desired_safety_factor - 0.1:
            bolt_comparison = "lower than desired"
        else:
            bolt_comparison = "within acceptable range"

        # Compare plate FOS
        if plate_fos > desired_safety_factor + 0.5:
            plate_comparison = "higher than desired"
        elif plate_fos < desired_safety_factor - 0.5:
            plate_comparison = "lower than desired"
        else:
            plate_comparison = "within acceptable range"

        return (
            f"The factor of safety for bolts is {bolt_fos:.2f} ({bolt_comparison}) and "
            f"the factor of safety for plates is {plate_fos:.2f} ({plate_comparison})."
        )


class VerboseAnalyticalTool(smolagents.tools.Tool):
    """
    A tool that calculates the factor of safety for a bolted connection using analytical expressions.

    This tool uses established engineering formulas to compute the factor of safety for a bolted connection
    based on the provided parameters.
    """

    name = "analytical_fos_calculation"
    description = "Calculates the factor of safety using analytical expressions."

    inputs = {
        "num_bolts": {
            "type": "number",
            "description": "Number of bolts used in the joint",
        },
        "bolt_diameter": {
            "type": "number",
            "description": "Diameter of the bolt in mm",
        }
    }

    output_type = "object"

    def __init__(self, joint_configuration: Dict[str, Any], tolerance: float = 0.1):
        super().__init__()
        self.tolerance = tolerance
        self.desired_safety_factor = joint_configuration["desired_safety_factor"]
        self.load = joint_configuration["load"]
        self.preload = joint_configuration["preload"]
        self.bolt_yield_strength = joint_configuration["bolt_yield_strength"]
        self.bolt_elastic_modulus = joint_configuration["bolt_elastic_modulus"]
        self.plate_thickness = joint_configuration["plate_thickness"]
        self.plate_elastic_modulus = joint_configuration["plate_elastic_modulus"]
        self.plate_yield_strength = joint_configuration["plate_yield_strength"]
        self.pitch = joint_configuration["pitch"]

    def forward(
        self,
        num_bolts: int,
        bolt_diameter: float,
    ) -> dict:

        load_per_bolt = self.load / num_bolts
        preload_per_bolt = self.preload / num_bolts
        tensile_area = get_tensile_stress_area(bolt_diameter, self.pitch)

        c = get_joint_constant(
            bolt_diameter,
            self.plate_thickness * 2,
            self.plate_elastic_modulus,
            self.bolt_elastic_modulus,
        )

        bolt_fos = bolt_yield_safety_factor(
            c=c,
            load=load_per_bolt,
            preload=preload_per_bolt,
            a_ts=tensile_area,
            b_ys=self.bolt_yield_strength,
        )

        bearing_area = bolt_diameter * self.plate_thickness * num_bolts
        bearing_stress = self.load / bearing_area
        allowable_bearing_stress = 1.5 * self.plate_yield_strength
        plate_fos = allowable_bearing_stress / bearing_stress

        bolt_diff = bolt_fos - self.desired_safety_factor
        plate_diff = plate_fos - self.desired_safety_factor

        return {
            "ok": (abs(bolt_diff) < self.tolerance) and (abs(plate_diff) < self.tolerance),
            "bolt_fos": bolt_fos,
            "bolt_diff": bolt_diff,
            "plate_fos": plate_fos,
            "plate_diff": plate_diff
        }