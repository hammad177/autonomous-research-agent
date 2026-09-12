from contextlib import asynccontextmanager, AsyncExitStack
from fastapi import FastAPI

from autonomous_research_agent.agents.checkpointer import sqlite_checkpointer
from autonomous_research_agent.agents.graph import build_research_graph
from autonomous_research_agent.api import (
    health,
    research,
    documents,
    graph,
    memory,
    runs,
)
from autonomous_research_agent.common.dependencies import (
    set_research_graph,
    get_vector_repository,
    get_graph_service,
    get_memory_service,
)
from autonomous_research_agent.mcp_server.tools import mcp


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        checkpointer = await stack.enter_async_context(sqlite_checkpointer())
        await checkpointer.setup()

        research_graph = build_research_graph(
            vector_repo=get_vector_repository(),
            graph_service=get_graph_service(),
            memory_service=get_memory_service(),
            checkpointer=checkpointer,
        )
        set_research_graph(research_graph)

        await stack.enter_async_context(mcp.session_manager.run())

        yield


app = FastAPI(title="Autonomous Research Agent", lifespan=lifespan)

app.include_router(health.router)
app.include_router(research.router)
app.include_router(documents.router)
app.include_router(graph.router)
app.include_router(memory.router)
app.include_router(runs.router)

app.mount("/", mcp.streamable_http_app())


def main():
    import uvicorn

    uvicorn.run(
        "autonomous_research_agent.main:app", host="0.0.0.0", port=8000, reload=True
    )


if __name__ == "__main__":
    main()
