import logging
from typing import Any, List, Dict, Union, Optional

from json_repair import json_repair

from app.domain.external.json_parser import JSONParser

logger = logging.getLogger(__name__)


class RepairJSONParser(JSONParser):
    async def invoke(self, text: str, default_value: Optional[Any] = None) -> Union[Dict, List, Any]:
        logger.info(f"RepairJSONParser invoke: {text}")
        if not text or not text.strip():
            if default_value is not None:
                return default_value
            raise ValueError("json text is empty, and not default value")
        return json_repair.repair_json(text, ensure_ascii=False)
