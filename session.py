# session.py

import asyncio
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# session.py
from db_base import Base  # ✅ Shared Base
# ... rest of your code remains the same ...

DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/mcdonald_agent"
Base = declarative_base()

class McSession(Base):
    __tablename__ = "mcdonald_agent_session"
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_conversation = Column(Text)
    order_detail = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class PostgreSQLSession:
    def __init__(self, session_id: str = None):
        self.session_id = session_id or str(uuid.uuid4())

    async def save(self, chat: str, order: str):
        async with AsyncSessionLocal() as session:
            async with session.begin():
                obj = await session.get(McSession, self.session_id)
                if obj:
                    obj.chat_conversation = chat
                    obj.order_detail = order
                    obj.timestamp = datetime.utcnow()
                else:
                    obj = McSession(session_id=self.session_id, chat_conversation=chat, order_detail=order)
                    session.add(obj)

    async def load(self):
        async with AsyncSessionLocal() as session:
            return await session.get(McSession, self.session_id)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Table created using SQLAlchemy")

async def preview_live_sessions():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(McSession).order_by(McSession.timestamp.desc())
        )
        rows = result.fetchall()
        for row in rows:
            data = row[0]
            print(f"\n🆔 {data.session_id}")
            print(f"💬 {data.chat_conversation}")
            print(f"📝 {data.order_detail}")
            print(f"⏰ {data.timestamp}")

# Optional testing:
# asyncio.run(init_db())
# asyncio.run(preview_live_sessions())
