from enum import Enum

class EnumHasValue(Enum):
    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_ 

class AIModel(str, EnumHasValue):
    """Enumeration of supported AI models."""
    
    # GPT-5 Series
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"
    
    # GPT-4.1 Series
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"
    
    # O Series
    O3 = "o3"
    O4_MINI = "o4-mini"

    # text-embedding-3
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
