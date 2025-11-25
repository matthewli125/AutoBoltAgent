import smolagents
from .low_fidelity_tool import FastenatingCalculator


class LowFidelityAgent(smolagents.MultiStepAgent):

    def __init__(self):
        tools = [FastenatingCalculator(env)]
        super().__init__(tools=tools)