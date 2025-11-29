import smolagents

import autoboltagent
import autoboltagent.prompts


def is_macos() -> bool:
    import platform

    return platform.system() == "Darwin"


def get_testing_model() -> smolagents.Model:
    if is_macos():
        # Use a local model on macOS for faster testing
        return smolagents.MLXModel(
            model_id="Qwen/Qwen3-1.7B-MLX-4bit",
        )
    else:
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
