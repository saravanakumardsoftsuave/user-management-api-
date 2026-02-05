import ssl
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
ssl_context = ssl.create_default_context()
# For Neon, use ssl=true in URL or configure connect_args
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"ssl": ssl_context}
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    try:
     async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        print(f"Error getting database session: {e}")
        raise e