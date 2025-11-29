import smolagents

import src.autoboltagent.fastener_toolkit as ft

class FastenatingCalculator(smolagents.Tool):
    name = "FOS_Calculation"
    description = "Calculates the factor of safety for fasteners using Yield Strength."

    inputs = {
        "desired_safety_factor": {
            "type": "number",
            "description": "Desired factor of safety",
        },
        "load": {
            "type": "number",
            "description": "Load applied to the bolt in Newtons",
        },
        "yield_strength": {
            "type": "number",
            "description": "Yield strength of the bolt material in MPa",
        },
        "preload": {
            "type": "number",
            "description": "Preload applied to the bolt in Newtons",
        },
        "pitch": {
            "type": "number",
            "description": "Pitch of the bolt in mm",
        },
        "E_b": {
            "type": "number",
            "description": "Young's modulus of the bolt in GPa",
        },
        "E_m": {
            "type": "number",
            "description": "Young's modulus of the material in GPa",
        },
        "l": {
            "type": "number",
            "description": "Clamped Length in mm",
        },
        "t_plate": {
            "type": "number",
            "description": "Thickness of the plate in mm",
        },
        "sigma_plate": {
            "type": "number",
            "description": "Yield strength of the plate material in MPa",
        },
        "d_major": {
            "type": "number",
            "description": "Major diameter of the bolt in mm",
        },
        "num_bolts": {
            "type": "number",
            "description": "Number of bolts used in the joint"
        },
    }

    output_type = "number"

    def forward(
            self,
            desired_safety_factor: float,
            d_major: float,
            load: float,
            yield_strength: float,
            preload: float,
            E_b: float,
            E_m: float,
            l: float,
            pitch: float,
            t_plate: float,
            sigma_plate: float,
            num_bolts: int) -> str:

        load_per_bolt = load / num_bolts
        preload_per_bolt = preload / num_bolts
        tensile_area = ft.get_tensile_stress_area(d_major, pitch)

        c = ft.get_joint_constant(d_major, l, E_m, E_b)

        bolt_sf = ft.bolt_yield_safety_factor(
            c=c, load=load_per_bolt, preload=preload_per_bolt, a_ts=tensile_area, b_ys=yield_strength)

        bearing_Area = d_major * t_plate * num_bolts
        bearing_stress = load / bearing_Area
        allowable_bearing_stress = 1.5 * sigma_plate
        plate_fs = allowable_bearing_stress / bearing_stress


        if bolt_sf > desired_safety_factor + 0.1:
            bolt_comparison = "higher than desired"
        elif bolt_sf < desired_safety_factor - 0.1:
            bolt_comparison = "lower than desired"
        else:
            bolt_comparison = "within acceptable range"

        # Compare plate FOS
        if plate_fs > desired_safety_factor + 0.5:
            plate_comparison = "higher than desired"
        elif plate_fs < desired_safety_factor - 0.5:
            plate_comparison = "lower than desired"
        else:
            plate_comparison = "within acceptable range"

        return (
            f"The factor of safety for bolts is {bolt_sf:.2f} ({bolt_comparison}) and "
            f"the factor of safety for plates is {plate_fs:.2f} ({plate_comparison})."
        )
