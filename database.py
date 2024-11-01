import yaml
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from models import Base


def load_config(config_file: str):
    with open(config_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config("config.yaml")

db_config = config["database"]


if db_config["dialect"] == "sqlite":
    db_url = f"sqlite+aiosqlite:///{db_config['database']}"
else:
    db_url = (
        f"{db_config['dialect']}+{db_config['driver']}://"
        f"{db_config['username']}:{db_config['password']}@"
        f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
    )

engine = create_async_engine(db_url, echo=False, future=True)


AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
