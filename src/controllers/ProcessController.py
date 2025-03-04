from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessingEnum

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)

    def get_file_extension(self, file_id: str):
        """Function to return file extention"""
        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):
        """Function to assign loader (from langchain) depond on the file extention"""
        file_ext = self.get_file_extension(file_id=file_id)

        # the text loader needs file path
        file_path = os.path.join(
            self.project_path,
            file_id
        )

        # here we handle 2 types of files (.txt, .pdf)
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding="utf-8")

        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        
        return None

    def get_file_content(self, file_id: str):

        # get suitable loader of file depending on the file type
        loader = self.get_file_loader(file_id=file_id)

        # return content
        return loader.load()

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=100, overlap_size: int=20):
        
        """Function to split the file content to chunks"""

        # create object from splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
        )

        # get list of loaded text
        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        # get list of loaded metadata for part
        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata
        )

        return chunks


    

