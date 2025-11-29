import smolagents

from .prompts import (
    TOOL_USING_INSTRUCTION,
    BASE_INSTRUCTIONS,
    DUAL_FIDELITY_COORDINATION,
)
from .tools import AnalyticalTool, FiniteElementTool


class GuessingAgent(smolagents.ToolCallingAgent):
    """
    An agent that makes guesses without using any tools.

    This agent operates solely based on its internal model and does not utilize any external tools for analysis or calculations.
    It is designed to provide initial estimates or solutions based on its knowledge and reasoning capabilities.
    """

    def __init__(self, model: smolagents.Model) -> None:
        """
        Initializes a GuessingAgent that does not use any tools.

        Args:
            model: An instance of smolagents.Model to be used by the agent.
        """
        super().__init__(
            name="GuessingAgent",
            tools=[],
            add_base_tools=False,
            model=model,
            instructions=BASE_INSTRUCTIONS,
        )


class LowFidelityAgent(smolagents.ToolCallingAgent):
    """
    An agent that utilizes a low-fidelity analytical tool for bolted connection design.

    This agent leverages an analytical tool to perform calculations and analyses related to bolted connections.
    It is designed to provide solutions based on simplified models and assumptions, making it suitable for quick estimates and preliminary designs.
    """

    def __init__(self, model: smolagents.Model) -> None:
        """
        Initializes a LowFidelityAgent that uses an analytical tool.

        Args:
            model: An instance of smolagents.Model to be used by the agent.
        """
        super().__init__(
            name="LowFidelityAgent",
            tools=[AnalyticalTool()],
            add_base_tools=False,
            model=model,
            instructions=BASE_INSTRUCTIONS + TOOL_USING_INSTRUCTION,
        )


class HighFidelityAgent(smolagents.ToolCallingAgent):
    """
    An agent that utilizes a high-fidelity finite element analysis tool for bolted connection design.

    This agent leverages a finite element tool to perform detailed calculations and analyses related to bolted connections.
    It is designed to provide accurate and reliable solutions based on comprehensive models, making it suitable for
    """

    def __init__(self, model: smolagents.Model) -> None:
        """
        Initializes a HighFidelityAgent that uses a finite element tool.

        Args:
            model: An instance of smolagents.Model to be used by the agent.
        """
        super().__init__(
            name="HighFidelityAgent",
            tools=[FiniteElementTool()],
            add_base_tools=False,
            model=model,
            instructions=BASE_INSTRUCTIONS + TOOL_USING_INSTRUCTION,
        )


class DualFidelityAgent(smolagents.ToolCallingAgent):
    """
    An agent that utilizes both low-fidelity and high-fidelity tools for bolted connection design.

    This agent leverages both an analytical tool and a finite element tool to perform calculations and analyses related to bolted connections.
    It is designed to provide solutions that balance speed and accuracy by using the low-fidelity tool
    """

    def __init__(self, model: smolagents.Model) -> None:
        """
        Initializes a DualFidelityAgent that uses both analytical and finite element tools.

        Args:
            model: An instance of smolagents.Model to be used by the agent.
        """
        super().__init__(
            name="DualFidelityAgent",
            tools=[AnalyticalTool(), FiniteElementTool()],
            add_base_tools=False,
            model=model,
            instructions=BASE_INSTRUCTIONS
            + TOOL_USING_INSTRUCTION
            + DUAL_FIDELITY_COORDINATION,
        )
