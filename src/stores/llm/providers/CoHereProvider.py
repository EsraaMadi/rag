from ..LLMInterface import LLMInterface
from ..LLMEnums import CoHereEnums, DocumentTypeEnum
import cohere
import logging

class CoHereProvider(LLMInterface):
    """Class for Cohere model (generation or embedding)"""
    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        """Function to set needed paramter for open AI model and initiate a client for the model"""

        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        # generation model
        self.generation_model_id = None

        # Embedding model
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = cohere.Client(api_key=self.api_key)

        self.enums = CoHereEnums
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        """Function to set model id for generation tasks"""
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Function to set model id for embedding tasks"""
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size

    def process_text(self, text: str):
        """Function to do needed preprocessing for text before use it"""
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        """Function to generate new text giving a query and chat history"""
        
        # check if the model client didn't setup correctly
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        # check if the model id didn't assign correctly
        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        # setup the max output token length / temp if it'nt the same as the one setted in the clearation of class object
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        # generate response using llm model
        response = self.client.chat(
            model = self.generation_model_id,
            chat_history = chat_history,
            message = self.process_text(prompt),
            temperature = temperature,
            max_tokens = max_output_tokens
        )

        # if the model does not return a response or it was empty
        if not response or not response.text:
            self.logger.error("Error while generating text with CoHere")
            return None
        
        # return the response if everyyhing went well
        return response.text
    
    def embed_text(self, text: str, document_type: str = None):
        """Function to get embedding vector of giving text"""

        # check if the model client didn't setup correctly
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None
        
        # check if the model id didn't assign correctly
        if not self.embedding_model_id:
            self.logger.error("Embedding model for CoHere was not set")
            return None
        
        # setup document type
        input_type = CoHereEnums.QUERY if document_type == DocumentTypeEnum.QUERY else CoHereEnums.DOCUMENT

        # generate embeddings using llm model
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)],
            input_type = input_type,
            embedding_types=['float'],
        )

        # if the model does not return a response or it was empty
        if not response or not response.embeddings or not response.embeddings.float:
            self.logger.error("Error while embedding text with CoHere")
            return None
        
        # return the response if everyyhing went well
        return response.embeddings.float[0]
    
    def construct_prompt(self, prompt: str, role: str):
        """Function to build required prompt format for the model history"""
        return {
            "role": role,
            "text": self.process_text(prompt)
        }