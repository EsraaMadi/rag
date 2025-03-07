from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

# Collection / table for the data chunks
class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # alias because if name it as _id it would be private and not accessable outsid class
    project_id: str = Field(..., min_length=1) # ... means any value , None , means could ne null

# when Field is not enpugh to write the validation rules
    @validator('project_id')
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        
        return value

    class Config:
        arbitrary_types_allowed = True
