from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """Interface class for all LLM providors, Note: all classes inhert from this interface (providors)
    have to implement these functions with same name (ensure consistency)"""
    @abstractmethod
    def set_generation_model(self, model_id: str):
        """Function to set model id for generation tasks"""
        pass

    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        """Function to set model id for embedding tasks"""
        pass

    @abstractmethod
    def generate_text(self, prompt: str, chat_history: list=[], max_output_tokens: int=None,
                            temperature: float = None):
        """Function to generate new text giving a query and chat history"""
        pass

    @abstractmethod
    def embed_text(self, text: str, document_type: str = None):
        """Function to get embedding vector of giving text"""
        pass

    @abstractmethod
    def construct_prompt(self, prompt: str, role: str):
        """Function to build required prompt format for the model"""
        pass
