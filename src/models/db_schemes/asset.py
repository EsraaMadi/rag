from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # alias because if name it as _id it would be private and not accessable outsid class
    asset_project_id: ObjectId  # its type of id that deal with mongo
    asset_type: str = Field(..., min_length=1) # ... means any value , None => means could ne null
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None) # greater than 0 , Field function help to put more condition on the paramter other than the type
    asset_config: dict = Field(default=None)
    asset_pushed_at: datetime = Field(default=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        """Function to define the index for this collection"""
        return [
            {
                "key": [
                    ("asset_project_id", 1) # 1 means ordered asc
                ],
                "name": "asset_project_id_index_1",
                "unique": False # could be repeated
            },
            {
                "key": [
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name": "asset_project_id_name_index_1",
                "unique": True # could be not repeated
            },
        ]