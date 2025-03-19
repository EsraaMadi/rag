from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy.future import select

class AssetModel(BaseDataModel):

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
    async def create_asset(self, asset: Asset):
        """
        Function to insert new asset in the db giving an asset object.
        
        Args:
            asset (Asset): The Asset object to be inserted
            
        Returns:
            Asset: The inserted asset with any database-generated values
        """
        async with self.db_client() as session:
            # Start a transaction
            async with session.begin():
                # Add the asset to the session
                session.add(asset)
            # Commit the transaction to persist changes
            await session.commit()
            # Refresh the object to get any database-generated values (like IDs)
            await session.refresh(asset)
        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        """
        Function to return all assets related to a project id filtered by asset type.
        
        Args:
            asset_project_id (str): The project ID to fetch assets for
            asset_type (str): The type of assets to filter by
            
        Returns:
            list: List of Asset objects matching the criteria
        """
        async with self.db_client() as session:
            # Create a SELECT statement with compound WHERE conditions
            # Filtering by both project ID and asset type
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_type == asset_type
            )
            # Execute the statement
            result = await session.execute(stmt)
            # Convert the result to a list of Asset objects
            records = result.scalars().all()
        return records

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        """
        Function to return a single asset identified by project id and asset name.
        
        Args:
            asset_project_id (str): The project ID to fetch the asset from
            asset_name (str): The name of the asset to retrieve
            
        Returns:
            Asset: The matching asset or None if not found
        """
        async with self.db_client() as session:
            # Create a SELECT statement with compound WHERE conditions
            # Using both project ID and asset name to uniquely identify the asset
            stmt = select(Asset).where(
                Asset.asset_project_id == asset_project_id,
                Asset.asset_name == asset_name
            )
            # Execute the statement
            result = await session.execute(stmt)
            # Get exactly one result or None if not found
            # scalar_one_or_none() will raise an exception if multiple records are found
            record = result.scalar_one_or_none()
        return record