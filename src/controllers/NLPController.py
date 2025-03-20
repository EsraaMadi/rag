from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json

class NLPController(BaseController):
    """
    Controller for managing NLP-related operations such as vector database management, 
    text embedding, semantic search, and answering RAG (Retrieval-Augmented Generation) questions.
    """

    def __init__(self, vectordb_client, generation_client, 
                 embedding_client, template_parser):
        """
        Initialize the NLPController with required clients and utilities.

        Args:
            vectordb_client: Client for managing vector database operations.
            generation_client: Client for generating text responses.
            embedding_client: Client for creating embeddings of text.
            template_parser: Template parser for constructing prompts.
        """

        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        """
        Generate a unique collection name for a project.

        Args:
            project_id (str): The unique ID of the project.

        Returns:
            str: The generated collection name.
        """
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        """
        Delete an existing collection in the vector database.

        Args:
            project (Project): The project for which the collection is to be deleted.

        Returns:
            bool: True if the collection was successfully deleted, False otherwise.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        """
        Retrieve information about a collection in the vector database.

        Args:
            project (Project): The project for which the collection info is to be retrieved.

        Returns:
            dict: A dictionary containing collection information.
        """
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads( # convert to json
            json.dumps(collection_info, default=lambda x: x.__dict__) # convert to string
        ) # to avoid errors
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk],
                                   chunks_ids: List[int], 
                                   do_reset: bool = False):
        """
        Index/insert text chunks into the vector database.

        Args:
            project (Project): The project for which the chunks are to be indexed.
            chunks (List[DataChunk]): A list of data chunks to be indexed.
            chunks_ids (List[int]): A list of IDs corresponding to the data chunks.
            do_reset (bool): Whether to reset the collection before indexing. Defaults to False.

        Returns:
            bool: True if the indexing was successful.
        """
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: generate embeddings then prepare inserted items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]

        # step3: create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # step4: insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True

    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        """
        Perform a semantic search in the vector database.

        Args:
            project (Project): The project for which the search is to be performed.
            text (str): The query text to search for.
            limit (int): The maximum number of results to retrieve. Defaults to 10.

        Returns:
            list or bool: A list of search results or False if no results are found.
        """
        # step1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # step2: get text embedding vector
        vector = self.embedding_client.embed_text(text=text, 
                                                 document_type=DocumentTypeEnum.QUERY.value)

        if not vector or len(vector) == 0:
            return False

        # step3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        if not results:
            return False

        return results
    
    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        """
        Generate an answer to a query using Retrieval-Augmented Generation (RAG).

        Args:
            project (Project): The project for which the query is being answered.
            query (str): The query text.
            limit (int): The number of related documents to retrieve for the query. Defaults to 10.

        Returns:
            tuple: A tuple containing the answer (str), the full prompt (str), and the chat history (list).
        """
        answer, full_prompt, chat_history = None, None, None

        # step1: retrieve related documents
        retrieved_documents = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step2: Construct LLM prompt

        # system prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        # body prompt
        documents_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx + 1,
                    "chunk_text": self.generation_client.process_text(doc.text),
            })
            for idx, doc in enumerate(retrieved_documents)
        ])

        # footer prompt
        footer_prompt = self.template_parser.get("rag", "footer_prompt", {
            "query": query
        })

        # step3: Construct Generation Client Prompts
        # we assign the system prompt to history
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n\n".join([ documents_prompts,  footer_prompt])

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )

        return answer, full_prompt, chat_history

