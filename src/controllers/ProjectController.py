from .BaseController import BaseController
import os

class ProjectController(BaseController):
    
    def __init__(self):
        super().__init__()

    def get_project_path(self, project_id: str):
        """Function to create a director of a project to save files on it"""
        project_dir = os.path.join(
            self.files_dir,
            project_id
        )

        # check if file is exist
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        return project_dir

    
