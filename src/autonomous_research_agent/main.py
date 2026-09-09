from fastapi import FastAPI
from autonomous_research_agent.api import health, research, documents

app = FastAPI(title="Autonomous Research Agent")

app.include_router(health.router)
app.include_router(research.router)
app.include_router(documents.router)


def main():
    import uvicorn

    uvicorn.run(
        "autonomous_research_agent.main:app", host="0.0.0.0", port=8000, reload=True
    )


if __name__ == "__main__":
    main()
