from functools import lru_cache
from typing import Dict
from backend.core.db.db_layer import read
from backend.core.db.db_layer import get_llm_config
class LLMConfig:
    _instance = None
    _config: Dict = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_config(cls) -> Dict:
        """Get cached config or load from DB"""
        if not cls._config:
            cls.load_config()
        return cls._config

    @classmethod
    def load_config(cls) -> Dict:                  
        cls._config = get_llm_config()
        return cls._config

    @classmethod
    def refresh(cls) -> Dict:
        """Force refresh config from database"""
        cls._config.clear()
        return cls.get_config()
