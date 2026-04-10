from duckduckgo_search import DDGS

def web_search(query: str, max_results=3) -> str:
    """Perform a web search using duckduckgo and return a text summary."""
    try:
        results = DDGS().text(query, max_results=max_results)
        if not results:
            return "No internet results found for this query."
        
        output = [f"Result: {r.get('title', '')}\nSnippet: {r.get('body', '')}\nURL: {r.get('href', '')}" for r in results]
        return "\n\n".join(output)
    except Exception as e:
        return f"Web search failed: {e}"
