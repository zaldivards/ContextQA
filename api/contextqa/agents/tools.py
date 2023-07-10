import requests
from bs4 import BeautifulSoup
from googlesearch import search
from langchain.agents import Tool

from contextqa import get_logger


LOGGER = get_logger()


def _get_content(url: str, timeout: int = 5) -> bytes:
    resp = requests.get(url=url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def _js_disable_message(text: str) -> bool:
    return "JavaScript is disabled in this browser" in text


def _searcher(search_term: str):
    """Search for the provided search term in Google Search when the assistant could not find information to answer"""
    results = search(search_term, num_results=5)
    for url in results:
        try:
            html_content = BeautifulSoup(_get_content(url), "html.parser")
        except requests.exceptions.HTTPError as ex:
            LOGGER.warning("Got HTTP error when requesting %s. Error %s", url, ex)
            continue
        else:
            html_text = html_content.text
            if _js_disable_message(html_text):
                LOGGER.warning("%s detected JavaScript not available", url)
                continue
            words = html_text.replace("\n", "").split()
            if len(words) > 100:
                LOGGER.info("Chosen url: %s", url)
                text = "I got the response:" + " ".join(words[:500])
                break
    return text


searcher = Tool(
    name="Crawl google for external knowledge",
    func=_searcher,
    description=(
        "useful for when the assitant does not know the answer of the human input and it needs external knowledge"
    ),
)
