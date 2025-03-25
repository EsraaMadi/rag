from enum import Enum

class VectorDBEnums(Enum):
    """ Enumeration for supported vector database implementations """
    QDRANT = "QDRANT"

class DistanceMethodEnums(Enum):
    """ Enumeration for distance calculation methods used in Qudrant vector similarity searches """
    COSINE = "cosine"
    DOT = "dot"
