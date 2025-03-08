from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]

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
        if DataBaseEnum.COLLECTION_ASSET_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSET_NAME.value]
            indexes = Asset.get_indexes() # get defined indexes
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    # all these functions should be async to avoid blocking
    async def create_asset(self, asset: Asset):
        """Function to insert new asset in the db giving an asset object"""
        # by_alias=True => to us _id instead of id aince the mangodb need it in this way
        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True))
        asset.id = result.inserted_id

        return asset

    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        """Function to return all assets related to an project id """

        records = await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type,
        }).to_list(length=None)

        return [
            Asset(**record)
            for record in records
        ]

    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        """Function to return asset related by project id and name """
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name,
        }) # it return one asset becase (project id, asset name) is unique

        if record:
            return Asset(**record)
        
        return None


    
