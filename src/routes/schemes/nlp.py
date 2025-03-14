from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
    """
    Model representing a request to push data into the vector database.

    Attributes:
        do_reset (Optional[int]): Indicates whether to reset the collection before pushing data.
                                  Defaults to 0 (no reset).
    """
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    """
    Model representing a request to search for similar vectors in the database.

    Attributes:
        text (str): The query text to search for similar vectors.
        limit (Optional[int]): The maximum number of results to return. Defaults to 5.
    """
    text: str
    limit: Optional[int] = 5
