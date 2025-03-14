from qdrant_client import models, QdrantClient
from ..VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
import logging
from typing import List
from models.db_schemes import RetrievedDocument

class QdrantDBProvider(VectorDBInterface):
    """ Qdrant db implementation for Abstract base class (VectorDBInterface) """
    
    def __init__(self, db_path: str, distance_method: str):
        """
        Initialize the vector database client.

        Args:
            db_path (str): The file path to the database.
            distance_method (str): The distance method to be used for similarity searches.
                                Should be one of the values from DistanceMethodEnums.
        """
        # Initialize the database client as None (to be set up later)
        self.client = None

        # Store the database path
        self.db_path = db_path

        # Initialize the distance method based on the input string
        self.distance_method = None
        if distance_method == DistanceMethodEnums.COSINE.value:
            # Set to cosine similarity if specified
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            # Set to dot product similarity if specified
            self.distance_method = models.Distance.DOT

        # Set up a logger for the class
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """ Establish a connection to the vector database."""
        self.client = QdrantClient(path=self.db_path)

    def disconnect(self):
        """ Close the connection to the vector database. """
        self.client = None

    def is_collection_existed(self, collection_name: str) -> bool:
        """
        Check if a collection with the specified name exists in the database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        return self.client.collection_exists(collection_name=collection_name)
    
    def list_all_collections(self) -> List:
        """
        Retrieve a list of all collections available in the database.

        Returns:
            List: A list of collection names.
        """
        return self.client.get_collections()
    
    def get_collection_info(self, collection_name: str) -> dict:
        """
        Retrieve metadata and information about a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            dict: A dictionary containing information about the collection.
        """
        return self.client.get_collection(collection_name=collection_name)
    
    def delete_collection(self, collection_name: str):
        """
        Delete a collection from the database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        if self.is_collection_existed(collection_name):
            return self.client.delete_collection(collection_name=collection_name)
        
    def create_collection(self, collection_name: str, 
                                embedding_size: int,
                                do_reset: bool = False):
        """
        Create a new collection in the database.

        Args:
            collection_name (str): The name of the new collection.
            embedding_size (int): The size of the embedding vectors to store.
            do_reset (bool, optional): If True, reset/delete the collection if it already exists. Defaults to False.
        """
        if do_reset:
            _ = self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed(collection_name):
            _ = self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                )
            )

            return True
        
        return False
    
    def insert_one(self, collection_name: str, text: str, vector: list,
                         metadata: dict = None, 
                         record_id: str = None):
        """
        Insert a single record into a collection.

        Args:
            collection_name (str): The name of the collection.
            text (str): The text data to associate with the vector.
            vector (list): The vector representation of the text.
            metadata (dict, optional): Additional metadata to store with the record. Defaults to None.
            record_id (str, optional): An optional unique identifier for the record. Defaults to None.
        """
        
        if not self.is_collection_existed(collection_name):
            self.logger.error(f"Can not insert new record to non-existed collection: {collection_name}")
            return False
        
        try:
            _ = self.client.upload_records(
                collection_name=collection_name,
                records=[
                    models.Record(
                        id=[record_id],
                        vector=vector,
                        payload={
                            "text": text, "metadata": metadata
                        }
                    )
                ]
            )
        except Exception as e:
            self.logger.error(f"Error while inserting batch: {e}")
            return False

        return True
    
    def insert_many(self, collection_name: str, texts: list, 
                          vectors: list, metadata: list = None, 
                          record_ids: list = None, batch_size: int = 50):
        """
        Insert multiple records into a collection in batches.

        Args:
            collection_name (str): The name of the collection.
            texts (list): A list of text data to associate with the vectors.
            vectors (list): A list of vector representations of the texts.
            metadata (list, optional): A list of metadata dictionaries for each record. Defaults to None.
            record_ids (list, optional): A list of unique identifiers for the records. Defaults to None.
            batch_size (int, optional): The size of each batch for insertion. Defaults to 50.
        """
        # these args are optional, in this case we need to make them consistance with other giving lists
        if metadata is None:
            metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = list(range(0, len(texts)))

        # loop over batches
        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            # identify batch records
            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_record_ids = record_ids[i:batch_end]

            # prepare list of records
            batch_records = [
                models.Record(
                    id=batch_record_ids[x],
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x], "metadata": batch_metadata[x]
                    }
                )

                for x in range(len(batch_texts))
            ]

            try:
                # insert the batch
                _ = self.client.upload_records(
                    collection_name=collection_name,
                    records=batch_records,
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

        return True
        
    def search_by_vector(self, collection_name: str, vector: list, limit: int = 5):
        """
        Search for the most similar vectors in a collection to the given vector.

        Args:
            collection_name (str): The name of the collection to search.
            vector (list): The query vector.
            limit (int): The maximum number of results to return.

        """
        results = self.client.search(
            collection_name=collection_name,
            query_vector=vector,
            limit=limit
        )

        if not results or len(results) == 0:
            return None
        
        return [
            RetrievedDocument(**{
                "score": result.score,
                "text": result.payload["text"],
            })
            for result in results
        ]

