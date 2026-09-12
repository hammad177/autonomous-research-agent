from contextlib import asynccontextmanager
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from autonomous_research_agent.config import settings


@asynccontextmanager
async def sqlite_checkpointer():
    async with AsyncSqliteSaver.from_conn_string(
        settings.CHECKPOINT_DB_PATH
    ) as checkpointer:
        yield checkpointer
