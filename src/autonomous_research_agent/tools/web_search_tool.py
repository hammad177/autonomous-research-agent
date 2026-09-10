from ddgs import DDGS
from langchain_core.tools import tool


def build_web_search_tool():
    """Builds and returns a configured web search tool."""

    @tool
    def web_search(query: str) -> str:
        """
        Search the live web for current, general, or external information
        not likely to be covered in the user's own knowledge base.
        Input should be a search query.
        """
        try:
            with DDGS() as ddgs:
                results = ddgs.text(query, max_results=5)
        except Exception as e:
            return f"Web search failed: {e}"

        if not results:
            return f"No search results found for '{query}'."

        formatted_results = []
        for i, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            href = result.get("href", "#")
            snippet = result.get("body", "No snippet available.")
            formatted_results.append(
                f"{i}. {title}\n" f"   URL: {href}\n" f"   Snippet: {snippet}\n"
            )

        return "\n".join(formatted_results)

    return web_search
