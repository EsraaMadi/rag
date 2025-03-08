from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value] # collection names saved in file


    @classmethod
    async def create_instance(cls, db_client: object):
        """Static Function (called without instant, using class name) used create an instance
          instead of regular "__init__" because we need to call the function that create the index
          in the creation instant but its async and could not called inside not async function __init__
           Note: can not convert __init__ to async
           Note: Now the creation of instance from this class in the main file would be using this fuction 
            instead of __init__ """
        instance = cls(db_client) # this function create instance from this class (this line call (__init__)
        await instance.init_collection() # call create index function for the collection
        return instance # return an instance from this class after initiated the needed collection and its index
    
    async def init_collection(self):
        """Function to create an index for the collection"""

        all_collections = await self.db_client.list_collection_names()
        # would be true only first time got a request from any one (in the begining of using the aplication)
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            indexes = Project.get_indexes() # get defined indexes
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    # all these functions should be async to avoid blocking
    async def create_project(self, project: Project):
        """Function to insert new project in the db giving a project object"""
        # by_alias=True => to us _id instead of id aince the mangodb need it in this way
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True))
        project.id = result.inserted_id

        return project

    async def get_project_or_create_one(self, project_id: str):
        """Function to return a chunk by id or insert new one if not exist"""
        record = await self.collection.find_one({
            "project_id": project_id
        })

        # if project id does not exist
        if record is None:
            # create new project
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)

            return project
        
        # it it exist
        return Project(**record) # record is dict type , cast it to project type

    async def get_all_projects(self, page: int=1, page_size: int=10):
        """Function to return group of projects by page number and page size """

        # count total number of documents
        total_documents = await self.collection.count_documents({})

        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0: # add an extra page for the remaining docs
            total_pages += 1

        # skip: help in stting the start point, limit: to limit the result
        cursor = self.collection.find().skip( (page-1) * page_size ).limit(page_size)
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )

        return projects, total_pages
