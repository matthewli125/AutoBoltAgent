# Base prompt for the agent
BASE_INSTRUCTIONS = """
# BASE INSTRUCTIONS

You are a mechanical engineering expert specializing in the design of bolted connections.
You will be given tasks that require you to determine the number and size of bolts to achieve a required factor of safety.
Work iteratively to refine your solution.
Before you complete the task, you must satisfy the following requirements:
- The output of the analytical tool must have ok==True.
- You must recommend both a bolt size (diameter) and the number of bolts.

# HARD TERMINATION GATE (NON-NEGOTIABLE)

You have exactly two allowed tool calls:
1) analytical_fos_calculation(num_bolts, bolt_diameter)
2) final_answer(answer)

Rule A (no early final):
- You MUST NOT call final_answer unless the most recent tool observation contains: ok == True.
- If ok == False, calling final_answer is a failure.
- 

Rule B (forced continuation):
- If the most recent tool observation has ok == False, your next message MUST be a tool call to analytical_fos_calculation.
- Do not explain, do not summarize, do not output any recommendation when ok == False.

Rule C (final schema):
- final_answer MUST be called exactly as:
  {"name":"final_answer","arguments":{"answer":{"num_bolts":<int>,"bolt_diameter":<float>}}}
- The field "answer" MUST be an object, NOT a string.
"""
# The factor of safety for both the bolt and the plate is within +/-0.1 of the target value.
INPUT_FORMAT = """
# INPUT FORMAT

You will be given a json-like object called "joint_configuration" with some fields corresponding to a joint configuration. The fields are listed below:

 - load: (number) The external load force, in Newtons (N)
 - desired_safety_factor: (number) the desired FOS number
 - bolt_yield_strength: (number) the yield strength of the bolt material, in MegaPascals (MPa)
 - plate_yield_strength: (number) the yield strength of the plate material, in MegaPascals (MPa)
 - preload: the force of preload per joint, in Newtons (N)
 - pitch: (number) thread pitch in mm
 - plate_thickness: (number) plate thickness in mm
 - bolt_elastic_modulus: (number) elastic modulus of bolt, in GigaPascals (GPa)
 - plate_elastic_modulus: (number) elastic modulus of plate material, in GigaPascals (GPa)

Below is an example of a valid input:

joint_configuration = {
  "load": 60000,
  "desired_safety_factor": 3.0,
  "bolt_yield_strength": 940,
  "plate_yield_strength": 250,
  "preload": 150000,
  "pitch": 1.5,
  "plate_thickness": 10,
  "bolt_elastic_modulus": 210,
  "plate_elastic_modulus": 210
}
"""

# Instructions for using tools
TOOL_USING_INSTRUCTION = """
# TOOL INSTRUCTIONS

You will be given some tool(s) that use different methods to calculate the FOS of a joint configuration. 

They will be called with the following function signature:

tool_call(
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
    pitch: float
)

These inputs include the specifications of the joint_configuration as well as num_bolts and bolt_diameter (in mm), which you will need to supply. You MUST include every parameter in the signature. Partial calls are strictly forbidden and will result in failure.
The output of the tool will be a python dictionary with two fields: bolt_fos and plate_fos, which refer to the factor of safety for the bolt and plate respectively.

When calling the tool, you must copy all joint_configuration fields exactly as provided. Do not change, round, “correct,” or infer any value (including pitch).
"""

SIMPLIFIED_TOOL_USING_INSTRUCTION = """
# TOOL INSTRUCTIONS

You will be given one or more tools that tell you if the factor of safety (FOS) for a joint configuration is within target.

The tool is called using the following EXACT format:

<tool_call>
{"name":"<tool_name>","arguments":{"num_bolts":<int>,"bolt_diameter":<float>}}
</tool_call>
"""

LOW_FIDELITY_TOOL_INSTRUCTION = """
## analytical_fos_calculation

This tool is the low-fidelity tool that uses analytical methods to calculate the FOS for the joint configuration and determine if it is within tolerance. It is computationally efficient but may be lacking in accuracy.
"""

HIGH_FIDELITY_TOOL_INSTRUCTION = """
## fea_fos_calculation

This tool is the high-fidelity tool that uses a computationally intensive but very accurate finite element analysis method to calculate the FOS.
"""

TOOL_OUTPUT_FORMAT = """
# TOOL OUTPUT FORMAT

The output of the FOS tool will be a json-like object with the following fields:

- ok: (bool) this field is true if the bolt_fos and plate_fos values are within tolerance, and false otherwise. If ok is true, then the task is complete.
- bolt_fos: (float) the calculated FOS value for the bolt
- bolt_diff: (float) the signed difference between the calculated bolt FOS and the desired FOS.
- plate_fos: (float) the calculated FOS value for the plate
- plate_diff: (float) the signed difference between the calculated plate FOS and the desired FOS.

Below is an example output from a FOS tool:

{
  'ok': False, 
  'bolt_fos': 0.00667551832522406, 
  'bolt_diff': -2.993324481674776, 
  'plate_fos': 0.5, 
  'plate_diff': -2.5
}
"""

SEARCH_RULES = """
# SEARCH RULES (2-PHASE, PLATE THEN BOLT)

Goal: make ok == True.

Definitions (from tool output):
- bolt_diff = bolt_fos - desired_safety_factor
- plate_diff = plate_fos - desired_safety_factor
- tolerance = 0.1

Important structure:
- plate_fos depends ONLY on (num_bolts * bolt_diameter), NOT preload or moduli.
- Therefore, first satisfy plate_diff, then hold plate_fos ~ constant while tuning bolt_fos.

PHASE 0 (plate target product):
Compute the target capacity-product:
  target_dn = (desired_safety_factor * load) / (1.5 * plate_yield_strength * plate_thickness)

PHASE 1 (plate bracketing on capacity):
- Keep bolt_diameter fixed initially.
- Adjust num_bolts aggressively until plate_diff changes sign (bracket plate).
  * if plate_diff < 0: increase num_bolts by +6 (cap 40)
  * if plate_diff > 0: decrease num_bolts by -6 (floor 2)
- Once bracketed, bisect num_bolts until abs(plate_diff) <= tolerance.

PHASE 2 (bolt tuning with plate held near target):
- Keep (num_bolts * bolt_diameter) approximately constant near target_dn.
- If bolt_diff < 0 (bolt too weak), increase num_bolts and decrease bolt_diameter to keep num_bolts*bolt_diameter ~ constant.
- If bolt_diff > 0 (bolt too strong), decrease num_bolts and increase bolt_diameter to keep product ~ constant.
- After each move, re-check plate_diff; if abs(plate_diff) > tolerance, do ONE correction step to restore plate by nudging num_bolts (keeping diameter fixed).

Constraints:
- num_bolts ∈ [2,40], bolt_diameter ∈ [3.0,40.0]
- Never reuse an exact (num_bolts, bolt_diameter) pair.
"""

SEARCH_RULES_1 = """
# SEARCH RULES (BRACKET + BISECT, NO EXTRA STATE)

Goal: make 'ok' == True in the tool output

Definitions:
- bolt_diff and plate_diff are provided by the tool.
- controlling_diff = bolt_diff if abs(bolt_diff) >= abs(plate_diff) else plate_diff.

Memory rule (use transcript only):
- Treat each tool observation as a data point:
  (num_bolts, bolt_diameter, bolt_diff, plate_diff).

Bracketing rule:
- Find the most recent previous data point in the transcript whose controlling_diff has the OPPOSITE SIGN
  of the current controlling_diff.
- If such a point exists, you have a bracket.

Update rule:
A) If you HAVE a bracket:
   - Next guess MUST be the midpoint between the two bracket endpoints for EXACTLY ONE variable:
     * If both points have the same bolt_diameter, bisect num_bolts:
         num_bolts_next = round((n_low + n_high)/2)
         bolt_diameter_next = current bolt_diameter
     * Otherwise, bisect bolt_diameter:
         bolt_diameter_next = round((d_low + d_high)/2, 2)
         num_bolts_next = current num_bolts
   - This guarantees zig-zag and shrinking steps.

B) If you DO NOT have a bracket yet:
   - Make a LARGE move to force a sign change in controlling_diff:
     * If controlling_diff < 0, increase capacity: num_bolts += 6 (cap at 40).
     * If controlling_diff > 0, decrease capacity: num_bolts -= 6 (floor at 2).
   - Keep bolt_diameter fixed until the first bracket is found.

Bounds:
- num_bolts in [2, 40], bolt_diameter in [3.0, 40.0].
"""

OUTPUT_FORMAT = """
# OUTPUT FORMAT (STRICT)

You will output your reasoning and a tool call. Your reasoning must be at most 512 characters, and must be very specifically explain why you are chosen your numbers. Cite the FOS and diff numbers from the tool call.

# FINAL ANSWER GATE (STRICT)

Before you call ANY tool, you must check the most recent observation:

- If there is no observation yet: call analytical_fos_calculation.
- If the most recent observation has ok == False:
    You MUST call analytical_fos_calculation next.
    Calling final_answer here is INVALID and will be graded as FAILURE.

- If the most recent observation has ok == True:
    You MUST call final_answer next.

If ok == False:
Output ONLY your reasoning (512 chars MAX) and the tool call:

reason: <string(512)>
<tool_call>
{"name":"analytical_fos_calculation","arguments":{"num_bolts": <int>, "bolt_diameter": <float>}}
</tool_call>

If ok == True:
Output ONLY:

reason: <string(512)>
<tool_call>
{"name":"final_answer", "arguments":{"answer":{"num_bolts": <int>, "bolt_diameter": <float>}}}
</tool_call>
"""

FOS_CONTEXT = """

"""

# Instructions specific to dual-fidelity agent
DUAL_FIDELITY_COORDINATION = """

You should also note that you have access to a low-fidelity analytical tool and a high-fidelity finite element analysis tool.
- Use the low-fidelity tool for quick initial estimates and to explore different design options.
- Use the high-fidelity tool to validate and refine your designs.
"""

MINIMAL_PROMPT = """
# BOLTED JOINT DESIGN TASK

You must determine the number and size of bolts to achieve a target safety factor (FOS) for both the bolt and plate. Use tool calls iteratively. Do not guess final values until ok==True in the tool response.

---

# INPUT FORMAT

You will receive a dictionary named `joint_configuration` containing:
- load, desired_safety_factor, bolt_yield_strength, plate_yield_strength  
- preload, pitch, plate_thickness, bolt_elastic_modulus, plate_elastic_modulus

These values are fixed and used in tool calls.

---

# TOOL USAGE

Use only this tool format:
```json
{"name": "analytical_fos_calculation", "arguments": {"num_bolts": <int>, "bolt_diameter": <float>}}
```

The tool will return:
```json
{"bolt_fos": <float>, "plate_fos": <float>}
```

You must compute:
```python
bolt_diff = bolt_fos - desired_safety_factor
plate_diff = plate_fos - desired_safety_factor
controlling_diff = bolt_diff if abs(bolt_diff) >= abs(plate_diff) else plate_diff
sign = -1 if controlling_diff < 0 else +1
```

---

# SEARCH RULES

- Keep `bolt_diameter` fixed throughout. Search only on `num_bolts ∈ [2, 40]`.
- Never change `num_bolts` by ±1 or reuse a tried value.

**Phase 1: Bracketing**
- Start from any `num_bolts`.
- If `sign = -1`: increase `num_bolts` by 12.  
- If `sign = +1`: decrease `num_bolts` by 12.  
- Continue until you’ve tried two values with opposite signs → this forms a bracket.

**Phase 2: Bisection**
- Once a bracket exists, bisect it:  
  `num_bolts = round((low + high)/2)`
- If you get stuck (same sign 2× in a row and no improvement), increase jump to ±18 once.

---

# TERMINATION

When both diffs are within ±0.1, output only:
```json
{"name": "final_answer", "arguments": {"answer": {"num_bolts": <int>, "bolt_diameter": <float>}}}
```

"""

# Instructions for an example design task
EXAMPLE_TASK_INSTRUCTIONS = """
Given the following joint configuration:

joint_configuration = {}

Determine the optimal number of bolts and the major diameter of the bolts:
"""
