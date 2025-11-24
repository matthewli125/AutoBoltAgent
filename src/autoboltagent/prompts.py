# test_0 = 'Calculate the optimal major diameter for a bolt given the following parameters: desired safety factor of 1.00, applied load of 5000 N, preload of 8000 N, pitch of 1.25 mm, elastic modulus of material is 200 GPa, Elastic Modulus of Bolt is 200 GPa, clamped length is 16 mm and yield strength of 350 MPa'

# test_1 = 'Determine the optimal major diameter for a bolt in a bolted flanged joint given the following parameters: Desired factor of safety is 2.50, Applied load of 7500 N, Preload of 11000 N, Pitch of 1.75 mm, Elastic modulus of the material is 190 GPa, Elastic modulus of the bolt is 205 GPa, Clamped length is 25 mm and Yield strength of the bolt material is 420 MPa'

# test_2 = "A mechanical assembly requires fastening two steel plates, each 15 mm thick, subjected to an axial tensile load of 25000 N. The joint uses a single bolt made of steel with a yield strength of 900 MPa and the desired factor of safety is 2.50. The bolt is preloaded to 40000 N. Determine the optimal bolt major diameter if clamped length is 30 mm, Pitch is 2.00 mm, Elastic Modulus of Bolt is 205 GPa, Elastic Modulus of Material is 205 GPa."

# test_3 = "A bolted clamped joint in a mechanical assembly is subjected to an axial tensile force due to externally applied loads. The joint consists of a high-strength bolt, which is preloaded to ensure sufficient clamping force while resisting additional applied forces. The connection also includes a spring washer, whose placement affects the force distribution and variation under cyclic loading. Determine the required major diameter if Initial Bolt Preload: 5000 N External Axial Load: 4000 N Desired Safety Factor: 3.50 Clamped Length: 20 mm Elastic modulus of bolt and material is 190 GPa Thread Pitch: 2.0 mm Yield Strength of Bolt Material: 600 MPa"

# test_4 = "An industrial motor weighing 60000 N is to be provided with a steel eye bolt for use when it is lifted. The bolt must be designed to sustain the axial tensile load without exceeding its yield strength, ensuring safe operation during lifting. A safety factor of 5.00 is desired to account for dynamic loading and impact forces associated with lifting operations. The class 10.9 steel bolt has a yield strength of 940 MPa. The preload is 80000 N, meaning only the external force due to the weight of the motor is considered. The thread pitch for an M18 bolt is 3 mm. The clamped length is around 50 mm and the elastic modulus f material and bolt is 190 GPa. Determine the required major diameter of the bolt that ensures safe lifting while maintaining the specified safety factor."

# test_5 = "A SAE Grade 5 UNF bolt is used in a mechanical joint to sustain a static tensile load of 15000 N. The desired safety factor is 4.50. The preload is 0 N. The proof strength (yield strength) of the bolt material is 550 MPa, and the thread pitch is 1.75 mm. The clamped length of the joint is 15 mm. The elastic modulus of the bolt is 200 GPa and the Elastic Modulus of the material is 200 GPa. Determine the optimal major diameter of the bolt."


## Using test_4 prompt for 30 questions

def generate_structured_prompts():
    # Define structured values
    loads = [30000, 60000]  # Two motor weights (loads)
    preloads = [80000, 150000]  # Two preloads
    clamped_lengths = [12,18,25]  # Four clamped lengths
    fos_values = [2.0, 3.0, 4.0] # Four FOS values
    # List to store all generated prompts
    prompts = []

    # Generate all possible combinations
    for load in loads:
        for preload in preloads:
            for clamped_length in clamped_lengths:
                for fos in fos_values:
                    ques = (
                    f"Given the following joint configuration:\n"
                    f"- External Load: {load} N\n"
                    f"- Desired Factor of Safety (FOS): {fos}\n"
                    f"- Bolt Material: 10.9 Steel (Yield Strength = 940 MPa)\n"
                    f"- Plate Material Yield Strength: 250 MPa\n"
                    f"- Preload per joint: {preload} N\n"
                    f"- Thread Pitch: 1.5 mm\n"
                    f"- Clamped Length: {clamped_length} mm\n"
                    f"- Plate Thickness: 10 mm\n"
                    f"- Elastic Modulus of Bolt: 210 GPa\n"
                    f"- Elastic Modulus of Plate Material: 210 GPa\n\n"
                    f"Determine the **optimal number of bolts** and the **major diameter of the bolt** such that "
                    f"**both the bolt and the plate have a factor of safety equal to {fos}**."
                )
                prompts.append((ques, load, preload, clamped_length, fos))

    return prompts