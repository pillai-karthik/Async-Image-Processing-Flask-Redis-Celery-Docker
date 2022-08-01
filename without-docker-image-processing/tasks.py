import time
from celery import Celery
from celery.utils.log import get_task_logger
from custom_image_processing import processImage

logger = get_task_logger(__name__)

app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@app.task()
def run_image_processing(UPLOAD_FOLDER, subfolderUniqueName, uploadedFileNewNameWithExtension ):
    logger.info('Got Request - Starting work ')

    time.sleep(5)
    final_folder_path=UPLOAD_FOLDER+"/"+subfolderUniqueName+"/"

    processImage(final_folder_path, uploadedFileNewNameWithExtension)

    logger.info('Work Finished ')

    result={}
    result["sub_upload_folder"]=subfolderUniqueName
    result["uploadedFileNewNameWithExtension"]=uploadedFileNewNameWithExtension

    return result
