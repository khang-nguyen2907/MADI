from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Interaction:
    """Record of a single interaction with the agent"""
    timestamp: datetime
    query: str
    plan: Dict[str, Any]