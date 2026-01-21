from sqlalchemy import create_engine

from sqlalchemy.orm import declarative_base, Session, sessionmaker, Mapped, mapped_column
from contextlib import contextmanager

from pathlib import Path

from datetime import datetime, timezone

Base = declarative_base()

class Iteration(Base):
    __tablename__ = "iterations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[str] = mapped_column()
    run_id: Mapped[str] = mapped_column()
    iteration_no: Mapped[int] = mapped_column()

    start_time: Mapped[datetime] = mapped_column(nullable=True)
    end_time: Mapped[datetime] = mapped_column(nullable=True)

    status: Mapped[str] = mapped_column(nullable=True)
    tool_call: Mapped[str] = mapped_column(nullable=True)
    observations: Mapped[str] = mapped_column(nullable=True)
    target_fos: Mapped[float] = mapped_column(nullable=True)

    failure_reason: Mapped[str] = mapped_column(nullable=True)
    llm_output: Mapped[str] = mapped_column(nullable=True)
    error_message: Mapped[str] = mapped_column(nullable=True)

class AgentLogger:
    _instance = None
    
    def connect_to_db(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url, future=True, pool_pre_ping=True)

        try:
            with self.engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
                conn.exec_driver_sql("PRAGMA synchronous=NORMAL;")

            Base.metadata.create_all(self.engine)

            self.db_session = sessionmaker(bind=self.engine, expire_on_commit=False, future=True)
        except Exception as e:
            raise IOError("Failed to connect to DB, check if file in use", repr(e))

    def __new__(cls, db_url: str):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.db_url = None
            cls._instance.engine = None
            cls._instance.db_session = None
            cls._instance.connect_to_db(db_url)
        return cls._instance
    
    @classmethod
    def reset(cls):
        if not cls._instance:
            return
        
        inst = cls._instance

        if inst.engine:
            inst.engine.dispose()
        
        if inst.db_url:
            for suffix in ("", "-wal", "-shm"):
                file_path = Path(inst.db_url.replace("sqlite:///", "") + suffix)
                file_path.unlink(missing_ok=True)

        cls._instance = None
    
    def log(
            self, 
            run_id, 
            agent_id, 
            target_fos,
            action_step
        ):

        iteration_no = action_step.step_number
        start_dt = datetime.fromtimestamp(action_step.timing.start_time, tz=timezone.utc)
        end_dt = datetime.fromtimestamp(action_step.timing.end_time, tz=timezone.utc)
        
        error = getattr(action_step, "error", None)
        tool_calls = getattr(action_step, "tool_calls", None)
        observations = getattr(action_step, "observations", None)
        llm_message = getattr(action_step, "model_output_message", None)
        llm_output = getattr(llm_message, "content", None)

        print(tool_calls)
        print(error)
        print(observations)
        print(llm_message)
        print(action_step.token_usage)

        try:

            with self.db_session() as session:
                session.add(
                    Iteration(
                        run_id=run_id,
                        agent_id=agent_id,
                        iteration_no=iteration_no,
                        start_time=start_dt,
                        end_time=end_dt,
                        tool_call=str(tool_calls[0] if tool_calls else None),
                        observations=observations,
                        target_fos=target_fos,
                        llm_output=llm_output,
                        error_message=error.message if (error and error.message) else None
                    )
                )
                session.flush()
                session.commit()

        except Exception as e:
            print("\n\n")
            print(e)
            print("\n\n")
        

            