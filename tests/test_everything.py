import autoboltagent
import autoboltagent.prompts

from smolagents import TransformersModel


def test_guessing_agent():

    # Use the smallest Instruct model available for fast CI feedback
    model = TransformersModel(
        model_id="HuggingFaceTB/SmolLM-135M-Instruct",
        max_new_tokens=200,  # Keep generation short for speed
    )

    # Create the GuessingAgent
    agent = autoboltagent.GuessingAgent(model)

    # Run it
    response = agent.run(autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS)

    # Make sure the response exists
    assert response is not None
