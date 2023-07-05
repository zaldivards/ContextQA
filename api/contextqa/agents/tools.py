import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain.agents import Tool


def _get_content(url: str, timeout: int = 5) -> bytes:
    resp = requests.get(url=url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def _searcher(search_term: str):
    results = search(search_term, num_results=1)
    first_result = next(results)
    html_content = BeautifulSoup(_get_content(first_result), "html.parser")
    return html_content.text


searcher = Tool(
    name="Response searcher",
    func=_searcher,
    description=(
        "useful for when the assitant does not know the answer for the human input and it needs external knowledge"
    ),
)
