
from .LLMEnums import LLMEnums
from .providers import OpenAIProvider, CoHereProvider

class LLMProviderFactory:
    """Class to manage utilizing all llm types"""
    def __init__(self, config: dict):
        """set the needed configration , generation model name , embedding model name"""
        self.config = config

    def create(self, provider: str):
        """Function to crate a providor object based on giving name"""

        # Open AI
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                api_key = self.config.OPENAI_API_KEY,
                base_url = self.config.OPENAI_API_URL,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            )

        # CoHere
        if provider == LLMEnums.COHERE.value:
            return CoHereProvider(
                api_key = self.config.COHERE_API_KEY,
                default_input_max_characters=self.config.INPUT_DAFAULT_MAX_CHARACTERS,
                default_generation_max_output_tokens=self.config.GENERATION_DAFAULT_MAX_TOKENS,
                default_generation_temperature=self.config.GENERATION_DAFAULT_TEMPERATURE
            )

        # if passed unsported llm name
        return None
