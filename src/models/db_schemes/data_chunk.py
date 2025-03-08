from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

# Collection / table for the data chunks
class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # alias because if name it as _id it would be private and not accessable outsid class
    chunk_text: str = Field(..., min_length=1) # ... means any value , None => means could ne null
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0) # greater than 0 , Field function help to put more condition on the paramter other than the type
    chunk_project_id: ObjectId # its type of id that deal with mongo
    chunk_asset_id: ObjectId

    class Config:
        arbitrary_types_allowed = True # this to avoid error that happen when pydantic does not know the type such as ObjectId

    @classmethod
    def get_indexes(cls):
        """Function to define the index for this collection"""
        return [
            {
                "key": [
                    ("chunk_project_id", 1) # 1 means ordered asc
                ],
                "name": "chunk_project_id_index_1",
                "unique": False # could be repeated
            }
        ]