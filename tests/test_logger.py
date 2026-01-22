from datetime import datetime, timezone

import pytest
from smolagents import (
    ActionStep,
    Timing,
    ToolCall,
    ChatMessage,
    MessageRole,
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from autoboltagent.tools.logger import AgentLogger
from autoboltagent.tools.logger import Iteration

db_url = "sqlite:///agent_logs_test.db"


@pytest.fixture
def logger():
    """
    Fixture to create a new AgentLogger with a fresh db per test
    """
    AgentLogger.reset()
    logger = AgentLogger(db_url)
    yield logger
    AgentLogger.reset()


def get_log_session(db_url):
    """
    Helper function to get db session from url
    """
    engine = create_engine(db_url)
    return Session(engine)


def test_logger_empty_when_fresh(logger):
    """
    Test to see if the logger db is empty when fresh
    """
    with get_log_session(db_url) as session:
        iterations = session.query(Iteration).all()

    assert len(iterations) == 0


def test_logger_one_write_fields_persist(logger):
    """
    Test one log write and see if all fields persists in the db
    """
    start_time = datetime.now(timezone.utc).timestamp()
    end_time = datetime.now(timezone.utc).timestamp()

    step = ActionStep(
        step_number=1,
        timing=Timing(start_time=start_time, end_time=end_time),
        observations="observation observation",
        tool_calls=[ToolCall(name="tool call", arguments={"asdf": 1}, id="1341fad")],
        model_output_message=ChatMessage(
            role=MessageRole("assistant"), content="LLM output 1"
        ),
        error=None,
    )

    logger.log(run_id="run_1", agent_id="agent_1", target_fos=1, action_step=step)

    with get_log_session(db_url) as session:
        iteration = session.query(Iteration).one()

        assert iteration.run_id == "run_1"
        assert iteration.agent_id == "agent_1"
        assert iteration.iteration_no == 1
        assert type(iteration.start_time) == datetime
        assert type(iteration.end_time) == datetime
        assert iteration.target_fos == 1
        assert iteration.llm_output == "LLM output 1"
        assert iteration.error_message == None


def test_logger_large_write(logger):
    """
    Test 50 log writes and see if db contains 50 rows
    """
    for i in range(50):
        start_time = datetime.now(timezone.utc).timestamp()
        end_time = datetime.now(timezone.utc).timestamp()
        step = ActionStep(
            step_number=1,
            timing=Timing(start_time=start_time, end_time=end_time),
            observations="observation observation",
            tool_calls=[
                ToolCall(name="tool call", arguments={"asdf": 1}, id="1341fad")
            ],
            model_output_message=ChatMessage(
                role=MessageRole("assistant"), content=f"LLM output {i}"
            ),
            error=None,
        )
        logger.log(run_id="run_1", agent_id="agent_1", target_fos=1, action_step=step)
    with get_log_session(db_url) as session:
        iterations = session.query(Iteration).all()

    assert len(iterations) == 50
