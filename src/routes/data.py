from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
from helpers.config import get_settings, Settings
from controllers import DataController, ProjectController, ProcessController
import aiofiles
from models import ResponseSignal
import logging
from .schemes.data import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.db_schemes import DataChunk

logger = logging.getLogger('uvicorn.error')

# modify the route/request
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)

# main body of request
@data_router.post("/upload/{project_id}")
async def upload_data(request: Request,project_id: str, file: UploadFile,
                      app_settings: Settings = Depends(get_settings)):

    # create project object
    project_model = ProjectModel(
        db_client=request.app.db_client   # request: has app object so we could retrive app paramters 
    )

    # insert project in db
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # validate the file properties (size, format)
    data_controller = DataController()

    is_valid, result_signal = data_controller.validate_uploaded_file(file=file)

    if not is_valid:
        # need this part to change the status of response
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": result_signal
            }
        )

    # if the file is valid , save it 
    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        # write file as chunckes
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    # when everything went well
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value,
                "file_id": file_id
            }
        )


@data_router.post("/process/{project_id}")
async def process_endpoint(request: Request, 
                           project_id: str, 
                           process_request: ProcessRequest):

    # the request bodey with be json that has the same paramter defined in the  ProcessRequest class
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    # create project object
    project_model = ProjectModel(
        db_client=request.app.db_client   # request: has app object so we could retrive app paramters 
    )

    # insert project in db or retiver it
    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    # start processing the file
    process_controller = ProcessController(project_id=project_id)

    # get file content
    file_content = process_controller.get_file_content(file_id=file_id)

    # process the file (spilt to chunks)
    file_chunks = process_controller.process_file_content(
        file_content=file_content,
        file_id=file_id,
        chunk_size=chunk_size,
        overlap_size=overlap_size
    )

    # in case the chunking process is faild
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    
    # prepare chunks to insert then in db
    file_chunks_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model = ChunkModel(
        db_client=request.app.db_client
    )

    # in case you want to clean the chunks for this project in the db first then insert new one
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    # inset chunks as bulk
    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )
