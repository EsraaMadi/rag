from .providers import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
from controllers.EmbedController import EmbedController

class VectorDBProviderFactory:
    """
    A factory class for creating instances of vector database providers.

    This class uses the configuration provided to determine which
    vector database provider to instantiate, based on the `provider` argument.
    """
    
    def __init__(self, config):
        """
        Initialize the factory with a configuration object.

        Args:
            config: A configuration object that contains the settings for the vector database.
        """
        self.config = config
        self.embed_controller = EmbedController()

    def create(self, provider: str):
        """
        Create and return a vector database provider instance based on the specified provider.

        Args:
            provider (str): The name of the vector database provider to create.
                            Should be one of the values from VectorDBEnums.

        Returns:
            An instance of the specified vector database provider (e.g., QdrantDBProvider) 
            or None if the provider is not supported.
        """
        # Check if the specified provider is QDRANT
        if provider == VectorDBEnums.QDRANT.value:
            # Retrieve the database path using BaseController
            db_path = self.embed_controller.get_database_path(db_name=self.config.VECTOR_DB_PATH)

            # Return an instance of QdrantDBProvider with the database path and distance method
            return QdrantDBProvider(
                db_path=db_path,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        
        # Return None if the specified provider is not supported
        return None
