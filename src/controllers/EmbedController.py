from .BaseController import BaseController
import os

class EmbedController(BaseController):
    
    def __init__(self):
        super().__init__()

    def get_database_path(self, db_name: str):
        """Function to create a director of a vector database to save embedding vectors on it"""
        database_path = os.path.join(
            self.database_dir, db_name
        )

        if not os.path.exists(database_path):
            os.makedirs(database_path)

        return database_path
