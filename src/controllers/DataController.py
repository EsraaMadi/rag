from .BaseController import BaseController
from .ProjectController import ProjectController
from fastapi import UploadFile
from models import ResponseSignal
import re
import os

class DataController(BaseController):
    
    def __init__(self):
        super().__init__() # initiate the parent class
        self.size_scale = 1048576 # used to convert MB to bytes

    def validate_uploaded_file(self, file: UploadFile):
        """
        Function to validate the type and size of uploaded file
        """

        # check file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return False, ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value

        if file.size > self.app_settings.FILE_MAX_SIZE * self.size_scale:
            return False, ResponseSignal.FILE_SIZE_EXCEEDED.value

        return True, ResponseSignal.FILE_VALIDATED_SUCCESS.value

    def generate_unique_filepath(self, orig_file_name: str, project_id: str):
        """Function to fix uploaded file name """

        # get random seq number 
        random_key = self.generate_random_string()

        # get the file location to store
        project_path = ProjectController().get_project_path(project_id=project_id)

        # get a new, fixed name for the file
        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )

        # create a full pathe (include name) for the file
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        # if the same file name is exist, keep generate anothe random number
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):
        """Function to fix uploaded file name """

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name


