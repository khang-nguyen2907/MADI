from typing import Optional, List
from pydantic import BaseModel

class PubmedSearchResult(BaseModel): 
    pubmed_id: Optional[str] = None
    title: Optional[str] = None
    keywords: Optional[List[str]] = None
    journals: Optional[str] = None 
    abstract: Optional[str] = None
    conclusions: Optional[str] = None
    methods: Optional[str] = None
    results: Optional[str] = None
    doi: Optional[str] = None

class DDuckGoSearchResult(BaseModel): 
    title: str
    url: str
    content: str

