# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from db_base import Base
from models import AgentSession  # ✅ This forces model import so Alembic can "see" it
from session import McSession    # ✅ Also load your session model if needed

target_metadata = Base.metadata
