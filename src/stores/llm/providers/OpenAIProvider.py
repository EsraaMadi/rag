from ..LLMInterface import LLMInterface
from ..LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    """Class for Open AI model (generation or embedding)"""
    def __init__(self, api_key: str, api_url: str=None,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        """Function to set needed paramter for open AI model and initiate a client for the model"""
        self.api_key = api_key
        self.api_url = api_url

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        # generation model
        self.generation_model_id = None

        # embedding model
        self.embedding_model_id = None
        self.embedding_size = None

        self.client = OpenAI(
            api_key = self.api_key,
            api_url = self.api_url
        )

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
            self.logger.error("OpenAI client was not set")
            return None

        # check if the model id didn't assign correctly
        if not self.generation_model_id:
            self.logger.error("Generation model for OpenAI was not set")
            return None
        
        # setup the max output token length / temp if it'nt the same as the one setted in the clearation of class object
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        # open ai need custom format for the input (the new message would be in the end of chat history)
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value) # put the user query in the needed format as well
        )

        # generate response using llm model
        response = self.client.chat.completions.create(
            model = self.generation_model_id,
            messages = chat_history,
            max_tokens = max_output_tokens,
            temperature = temperature
        )

        # if the model does not return a response or it was empty
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error("Error while generating text with OpenAI")
            return None

        # return the response if everyyhing went well
        return response.choices[0].message["content"]


    def embed_text(self, text: str, document_type: str = None):
        """Function to get embedding vector of giving text"""

        # check if the model client didn't setup correctly
        if not self.client:
            self.logger.error("OpenAI client was not set")
            return None

        # check if the model id didn't assign correctly
        if not self.embedding_model_id:
            self.logger.error("Embedding model for OpenAI was not set")
            return None
        
        # generate the embeddings using llm model
        response = self.client.embeddings.create(
            model = self.embedding_model_id,
            input = text,
        )

        # if the model does not return a response or it was empty
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            return None

        # return the response if everyyhing went well
        return response.data[0].embedding

    def construct_prompt(self, prompt: str, role: str):
        """Function to build required prompt format for the model"""
        return {
            "role": role,
            "content": self.process_text(prompt)
        }
    


    

