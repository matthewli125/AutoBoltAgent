import smolagents

import autoboltagent

# Use a local model on macOS for faster testing
model = smolagents.MLXModel(
    model_id="mlx-community/Qwen3-4B-Instruct-2507-4bit",
    max_tokens=2000,
)

autoboltagent.HighFidelityAgent(model).run(
    autoboltagent.prompts.EXAMPLE_TASK_INSTRUCTIONS
)
