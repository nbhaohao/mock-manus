from typing import Protocol, Optional, Any, List, Dict, Union


class JSONParser(Protocol):

    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]: \
            ...
