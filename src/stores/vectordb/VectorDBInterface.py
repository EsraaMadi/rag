from abc import ABC, abstractmethod
from typing import List
 

class VectorDBInterface(ABC):
    """
    Abstract base class for a vector database interface. 
    This defines the required methods that any concrete implementation must provide.
    """

    @abstractmethod
    def connect(self):
        """ Establish a connection to the vector database."""
        pass

    @abstractmethod
    def disconnect(self):
        """ Close the connection to the vector database. """
        pass

    @abstractmethod
    def is_collection_existed(self, collection_name: str) -> bool:
        """
        Check if a collection with the specified name exists in the database.

        Args:
            collection_name (str): The name of the collection to check.

        Returns:
            bool: True if the collection exists, False otherwise.
        """
        pass

    @abstractmethod
    def list_all_collections(self) -> List:
        """
        Retrieve a list of all collections available in the database.

        Returns:
            List: A list of collection names.
        """
        pass

    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        """
        Retrieve metadata and information about a specific collection.

        Args:
            collection_name (str): The name of the collection.

        Returns:
            dict: A dictionary containing information about the collection.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        """
        Delete a collection from the database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        """
        Search for the most similar vectors in a collection to the given vector.

        Args:
            collection_name (str): The name of the collection to search.
            vector (list): The query vector.
            limit (int): The maximum number of results to return.

        """
        pass