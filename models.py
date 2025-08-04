# models.py
from sqlalchemy import Column, Integer, String, DateTime, func
from db_base import Base  # ✅ Shared Base

class AgentSession(Base):
    __tablename__ = 'agent_sessions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String)
    user_name = Column(String)
    user_phone = Column(String)
    user_address = Column(String)
    order_type = Column(String)
    user_order = Column(String)
    chat_text = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
