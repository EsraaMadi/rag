from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select
from sqlalchemy import func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        """Static Function (called without instant, using class name) used create an instance
          instead of regular "__init__" because we need to call the function that create the index
          in the creation instant but its async and could not called inside not async function __init__
           Note: can not convert __init__ to async
           Note: Now the creation of instance from this class in the main file would be using this fuction 
            instead of __init__ """
        instance = cls(db_client) # this function create instance from this class (this line call (__init__)
        return instance # return an instance from this class after initiated the needed collection and its index
    

    # all these functions should be async to avoid blocking
    async def create_project(self, project: Project):
        """Function to insert new project in the db giving a project object"""
        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        
        return project

    async def get_project_or_create_one(self, project_id: str):
        """
        Function to return a project by id or insert a new one if it doesn't exist.
        
        This implements the common pattern of "get or create" to ensure we always
        have a project object to work with.
        
        Args:
            project_id (str): The unique identifier for the project to retrieve or create
            
        Returns:
            Project: An existing or newly created project object
        """
        async with self.db_client() as session:
            # Start a transaction - ensures atomicity of the get-or-create operation
            async with session.begin():
                # Build query to find project by project_id
                query = select(Project).where(Project.project_id == project_id)
                
                # Execute query
                result = await session.execute(query)
                
                # Get the project or None if it doesn't exist
                # scalar_one_or_none() returns exactly one result or None (raises error if multiple found)
                project = result.scalar_one_or_none()
                
                # If the project doesn't exist, create a new one
                if project is None:
                    # Create a new Project instance with the provided ID
                    project_rec = Project(
                        project_id=project_id
                    )
                    
                    # Use the existing create_project method to insert the new project
                    # This likely handles session management and any additional logic
                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    # Return the existing project
                    return project


    async def get_all_projects(self, page: int=1, page_size: int=10):
        """
        Function to return group of projects by page number and page size.
        
        Args:
            page (int): The page number to retrieve (1-indexed). Defaults to 1.
            page_size (int): Number of projects per page. Defaults to 10.
            
        Returns:
            tuple: (list of Project objects, total number of pages)
        """
        
        async with self.db_client() as session:
            # Start a transaction
            async with session.begin():
                
                # Count the total number of projects in the database
                total_documents = await session.execute(select(
                    func.count(Project.project_id)
                ))
                
                # Extract the scalar count value from the result
                total_documents = total_documents.scalar_one()
                
                # Calculate total pages needed for pagination
                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    # Add an extra page if there's a remainder
                    total_pages += 1
                
                # Build query with pagination: select projects with offset and limit
                query = select(Project).offset((page - 1) * page_size).limit(page_size)
                
                # Execute query and fetch all projects for the current page
                projects = await session.execute(query)
                projects = projects.scalars().all()
                
                # Return both the projects and the total page count
                return projects, total_pages
