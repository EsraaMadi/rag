from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from sqlalchemy.future import select
from sqlalchemy import func, delete

class ChunkModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        """Static Function (called without instant, using class name) used create an instance
          instead of regular "__init__" because we need to call the function that create the index
          in the creation instant but its async and could not called inside not async function __init__
           Note: can not convert __init__ to async
           Note: Now the creation of instance from this class in the main file would be using this fuction 
            instead of __init__ """
        instance = cls(db_client) # this function create instance from this class (this line call (__init__)
        return instance # return an instance from this class after initiated the needed collection and its index



    # all these functions should be async to avoid blocking
    async def create_chunk(self, chunk: DataChunk):
        """
        Function to insert new chunk in the db giving a datachunk object.
        
        Args:
            chunk (DataChunk): The DataChunk object to be inserted
            
        Returns:
            DataChunk: The inserted chunk with any database-generated values
        """
        async with self.db_client() as session:
            # Start a transaction
            async with session.begin():
                # Add the chunk to the session
                session.add(chunk)
            # Commit the transaction to persist changes
            await session.commit()
            # Refresh the object to get any database-generated values
            await session.refresh(chunk)
        return chunk

    async def get_chunk(self, chunk_id: str):
        """
        Function to return a chunk by id.
        
        Args:
            chunk_id (str): The unique identifier of the chunk to retrieve
            
        Returns:
            DataChunk: The retrieved chunk or None if not found
        """
        async with self.db_client() as session:
            # Execute query to find chunk by chunk_id
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id))
            # Get exactly one result or None if not found
            chunk = result.scalar_one_or_none()
        return chunk

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):
        """
        Function to insert group of chunks together in db giving a list of text.
        Performs batch inserts for better performance.
        
        Args:
            chunks (list): List of DataChunk objects to insert
            batch_size (int): Number of chunks to insert in each batch, defaults to 100
            
        Returns:
            int: Total number of chunks inserted
        """
        async with self.db_client() as session:
            async with session.begin():
                # Process chunks in batches of batch_size
                for i in range(0, len(chunks), batch_size):
                    # Extract the current batch
                    batch = chunks[i:i+batch_size]
                    # Add all chunks in the batch to the session
                    session.add_all(batch)
            # Commit all batches in one transaction
            await session.commit()
        return len(chunks)

    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """
        Function to delete group of chunks in db by project id.
        
        Args:
            project_id (ObjectId): The project ID whose chunks should be deleted
            
        Returns:
            int: Number of chunks deleted
        """
        async with self.db_client() as session:
            # Create a DELETE statement with WHERE condition
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            # Execute the statement
            result = await session.execute(stmt)
            # Commit the changes
            await session.commit()
        # Return the number of rows affected
        return result.rowcount

    async def get_poject_chunks(self, project_id: ObjectId, page_no: int=1, page_size: int=50):
        """
        Function to retrieve chunks belonging to a specific project with pagination.
        
        Args:
            project_id (ObjectId): The project ID to fetch chunks for
            page_no (int): The page number to retrieve (1-indexed), defaults to 1
            page_size (int): Number of chunks per page, defaults to 50
            
        Returns:
            list: List of DataChunk objects for the specified project and page
        """
        async with self.db_client() as session:
            # Create a SELECT statement with WHERE condition and pagination
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            # Execute the statement
            result = await session.execute(stmt)
            # Convert the result to a list of DataChunk objects
            records = result.scalars().all()
        return records