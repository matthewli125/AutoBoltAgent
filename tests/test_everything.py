import smolagents

import autoboltagent
import autoboltagent.prompts


def get_testing_model() -> smolagents.Model:
    # Use the smallest Instruct model available for fast CI feedback
    return smolagents.TransformersModel(
        model_id="HuggingFaceTB/SmolLM-135M-Instruct",
        max_new_tokens=200,  # Keep generation short for speed
    )


def test_guessing_agent():

    # Create the GuessingAgent and run it
    response = autoboltagent.GuessingAgent(get_testing_model()).run(
        autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS
    )

    # Make sure the response exists
    assert response is not None


def test_low_fidelity_agent():

    # Create the LowFidelityAgent and run it
    response = autoboltagent.LowFidelityAgent(get_testing_model()).run(
        autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS
    )

    # Make sure the response exists
    assert response is not None


def test_high_fidelity_agent():

    # Create the HighFidelityAgent and run it
    response = autoboltagent.HighFidelityAgent(get_testing_model()).run(
        autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS
    )

    # Make sure the response exists
    assert response is not None


def test_dual_fidelity_agent():

    # Create the DualFidelityAgent and run it
    response = autoboltagent.DualFidelityAgent(get_testing_model()).run(
        autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS
    )

    # Make sure the response exists
    assert response is not None
