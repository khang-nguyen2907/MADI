from phi.tools.duckduckgo import DuckDuckGo
from duckduckgo_search import DDGS
from typing import List, Dict
from madi.utils import tool
from madi.schema import DDuckGoSearchResult
from madi.utils import load_default_config

configs = load_default_config()

def phi_duckgo_search():
    return DuckDuckGo()

@tool()
def duckgo_search(query: str) -> List[DDuckGoSearchResult]: 
    """Searches DuckDuckGo for text-based information related to the given query.
    
    Parameters:
        - query: The search query string. This could be a complete sentence or keyword
    """
    results = []
    info = DDGS().text(query, max_results=configs["madi_configs"]["doc_search"]["max_internet_docs"])
    for data in info: 
        result = DDuckGoSearchResult(
            title=data["title"], 
            url=data["href"], 
            content=data["body"]
        )
        results.append(result)
    return results

