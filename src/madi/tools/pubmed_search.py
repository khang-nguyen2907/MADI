from phi.tools.pubmed import PubmedTools
from pymed import PubMed
from typing import (
    Dict, 
    Any, 
    List
)
from madi.utils import tool
from madi.schema import PubmedSearchResult
from madi.constants import ENV_VAR
from madi.utils import load_default_config

configs = load_default_config()

def phi_pubmed_search():
    return PubmedTools()

@tool()
def search_pubmed(search_term: str) -> List[PubmedSearchResult]:
    """Searches PubMed for medical articles and journals related to the given search term.

    Parameters:
        - search_term: The keywords to search for in PubMed. It should be a keyword or key phrase
    """
    pubmed = PubMed(tool="PubMedSearcher", email=ENV_VAR["EMAIL"])
    results = pubmed.query(search_term, max_results=configs["madi_configs"]["doc_search"]["max_pubmed_docs"])
    articleList = []
    articleInfo = []

    for article in results:
    # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
    # We need to convert it to dictionary with available function
        articleDict = article.toDict()
        articleList.append(articleDict)
    # Generate list of dict records which will hold all article details that could be fetch from PUBMED API
    for article in articleList:
    #Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list - thats article pubmedId
        pubmedId = article['pubmed_id'].partition('\n')[0]
        # Append article info to dictionary
        articleInfo.append(
            PubmedSearchResult(
                pubmed_id=pubmedId,
                title=article['title'],
                keywords=article['keywords'],
                journals=article['journal'],
                abstract=article['abstract'],
                conclusions=article['conclusions'],
                methods=article['methods'],
                results=article['results'],
                doi=article['doi']
            )
        )
    return articleInfo