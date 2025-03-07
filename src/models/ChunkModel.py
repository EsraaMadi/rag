from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    # all these functions should be async to avoid blocking
    async def create_chunk(self, chunk: DataChunk):
        """Function to insert new chunk in the db giving a datachunk object"""
        # by_alias=True => to us _id instead of id aince the mangodb need it in this way
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk

    async def get_chunk(self, chunk_id: str):
        """Function to return a chunk by id"""
        result = await self.collection.find_one({
            "_id": ObjectId(chunk_id) # casting the id to type in the mongodb
        })

        # if the chunk id does not exist
        if result is None:
            return None
        
        return DataChunk(**result) # result is dict type , cast it to datachunck type

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):
        """Function to insert group of chunks together in db giving a list of text"""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            # create insert object for each chunk
            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)
        
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """Function to delete group of chunks in db by project id"""
        result = await self.collection.delete_many({
            "chunk_project_id": ObjectId(project_id)
        })

        return result.deleted_count
    
    

    
