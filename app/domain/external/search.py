from typing import Protocol, Optional

from models.search import SearchResults
from models.tool_result import ToolResult


class SearchEngine(Protocol):

    async def invoke(self, query: str, date_range: Optional[str] = None) -> ToolResult[SearchResults]:
        ...
