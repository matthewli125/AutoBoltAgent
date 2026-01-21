import smolagents

from .verbose_prompts import (
    TOOL_USING_INSTRUCTION,
    SIMPLIFIED_TOOL_USING_INSTRUCTION,
    BASE_INSTRUCTIONS,
    INPUT_FORMAT,
    OUTPUT_FORMAT,
    LOW_FIDELITY_TOOL_INSTRUCTION,
    EXAMPLE_TASK_INSTRUCTIONS
)
from .tools.low_fidelity_tool import VerboseAnalyticalTool

from .tools.logger import AgentLogger


class VerboseLowFidelityAgent(smolagents.agents.ToolCallingAgent):
    def __init__(self, model: smolagents.models.Model, joint_configuration: dict, agent_id: str, run_id: str, target_fos: float, agent_logger: AgentLogger|None = None) -> None:
        
        self.agent_logger = agent_logger
        self.agent_id = agent_id
        self.run_id = run_id
        self.target_fos = target_fos

        callbacks = [self.log] if self.agent_logger else []
        super().__init__(
            name="VerboseLowFidelityAgent",
            tools=[VerboseAnalyticalTool(joint_configuration)],
            add_base_tools=False,
            model=model,
            instructions=(
                BASE_INSTRUCTIONS + 
                INPUT_FORMAT +
                OUTPUT_FORMAT +
                SIMPLIFIED_TOOL_USING_INSTRUCTION + 
                LOW_FIDELITY_TOOL_INSTRUCTION
            ),
            step_callbacks=callbacks,
            verbosity_level=2,
        )

    def log(self, step, agent):
        if self.agent_logger and  step.__class__.__name__ == "ActionStep":
            self.agent_logger.log(
                agent_id=self.agent_id, 
                run_id=self.run_id, 
                target_fos=self.target_fos, 
                action_step=step
            )