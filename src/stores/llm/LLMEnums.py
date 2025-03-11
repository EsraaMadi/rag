from enum import Enum

class LLMEnums(Enum):
    """All LLm providors"""
    OPENAI = "OPENAI"
    COHERE = "COHERE"

class OpenAIEnums(Enum):
    """Open AI role types"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CoHereEnums(Enum):
    """CoHere role types & text types"""
    SYSTEM = "SYSTEM"
    USER = "USER"
    ASSISTANT = "CHATBOT"

    DOCUMENT = "search_document"
    QUERY = "search_query"


class DocumentTypeEnum(Enum):
    """Text types"""
    DOCUMENT = "document"
    QUERY = "query"