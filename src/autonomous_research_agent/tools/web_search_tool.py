"""Live web search tool for current or general external information."""

from langchain_community.tools import DuckDuckGoSearchRun


def build_web_search_tool():
    search = DuckDuckGoSearchRun()
    search.name = "web_search"
    search.description = (
        "Search the live web for current, general, or external information "
        "not likely to be covered in the user's own knowledge base."
    )
    return search
