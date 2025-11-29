import autobolt
import smolagents
from .inputs import INPUTS


class FiniteElementTool(smolagents.Tool):
    """
    A tool that calculates the factor of safety for a bolted connection using finite element analysis.

    This tool leverages the autobolt library to perform finite element calculations and determine the factor of safety
    for a bolted connection based on the provided parameters.
    """

    name = "fea_fos_calculation"
    description = "Calculates the factor of safety using finite element analysis."

    inputs = INPUTS

    output_type = "number"

    def forward(
        self,
        desired_safety_factor: float,
        load: float,
        preload: float,  # not used but kept for interface consistency
        num_bolts: int,
        bolt_diameter: float,
        bolt_yield_strength: float,  # not used but kept for interface consistency
        bolt_elastic_modulus: float,  # not used but kept for interface consistency
        plate_thickness: float,
        plate_elastic_modulus: float,
        plate_yield_strength: float,
        pitch: float,  # not used but kept for interface consistency
    ) -> str:

        # Define dimensions of the plate
        plate_width = 0.1  # [m]
        plate_length = 0.2  # [m]

        sf = autobolt.calculate_fos(
            plate_thickness_m=plate_thickness,
            num_holes=num_bolts,
            elastic_modulus=plate_elastic_modulus,
            yield_strength=plate_yield_strength,
            traction_values=[(0, -load, 0)],
            hole_radius_m=bolt_diameter / 2,
            plate_length_m=plate_length,
            plate_width_m=plate_width,
            edge_margin_m=plate_length / (2 * num_bolts),
            hole_spacing_m=plate_length / num_bolts,
            hole_offset_from_bottom_m=0.020,  # [m] vertical position of hole centers (Y from bottom edge)
            plate_gap_mm=0.01,  # [mm] gap between the two plates
            poissons_ratio=0.3,  # Poisson's ratio for steel
        )

        if sf > desired_safety_factor + 0.1:
            comparison = "higher than desired"
        elif sf < desired_safety_factor - 0.1:
            comparison = "lower than desired"
        else:
            comparison = "within acceptable range"

        return f"The factor of safety for the assembly is {sf:.2f} ({comparison})."
