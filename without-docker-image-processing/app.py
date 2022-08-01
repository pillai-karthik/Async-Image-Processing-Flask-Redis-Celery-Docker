from flask import Flask, jsonify, flash, request, redirect, send_from_directory
from celery import Celery
from werkzeug.utils import secure_filename
import re
import random
from datetime import datetime
import pathlib

app = Flask(__name__)
simple_app = Celery('simple_worker', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = './uploaded_images'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/test', methods=['GET'])
def test_api():
    return "Success"


@app.route('/upload-file-async', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        uploadedFile = request.files['image']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploadedFile.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if uploadedFile and allowed_file(uploadedFile.filename):

            uploadedFilenameWithExt = secure_filename(uploadedFile.filename)
            uploadedFileExtension=uploadedFilenameWithExt.split(".")[-1]

            currentTime = re.sub('-| |:','_',str(datetime.now()))[:19]
            randomNumber = random.randint(10000000000,99999999999)

            subfolderUniqueName=currentTime+"-"+str(randomNumber)
            uploadedFileNewNameWithExtension="input."+uploadedFileExtension
            
            pathlib.Path(UPLOAD_FOLDER+"/"+subfolderUniqueName+"/").mkdir(parents=True, exist_ok=True) 

            uploadImageFilePath=UPLOAD_FOLDER+"/"+subfolderUniqueName+"/"+uploadedFileNewNameWithExtension
            uploadedFile.save(uploadImageFilePath)

            responseTask = simple_app.send_task('tasks.run_image_processing', 
                                                kwargs={
                                                    'UPLOAD_FOLDER': UPLOAD_FOLDER, 
                                                    'subfolderUniqueName':subfolderUniqueName,
                                                    'uploadedFileNewNameWithExtension': uploadedFileNewNameWithExtension})

            response={}
            response["task-id"]=responseTask.id
            response["message"]="Image is added to queue for processing!"
            response["task-response-status-url"]=request.host_url+"result/"+responseTask.id

            return response


@app.route('/result/<task_id>')
def get_task_result(task_id):
    status = simple_app.AsyncResult(task_id, app=simple_app)

    if str(status.state)=="SUCCESS":
        result = simple_app.AsyncResult(task_id).result

        response={}
        response["output-image"]=request.host_url+"output/"+result["sub_upload_folder"]+"/"+result["uploadedFileNewNameWithExtension"]
        response["output-image-procesed"]=request.host_url+"output/"+result["sub_upload_folder"]+"/processed-"+result["uploadedFileNewNameWithExtension"]
        
        return jsonify(response), 200

    elif str(status.state)=="PENDING":
        response={}
        response["Message"]="Processing Images. Please wait!"
        return jsonify(response), 202

    elif str(status.state)=="FAILURE":
        response={}
        response["Message"]="Failed to Process Images!"
        return jsonify(response), 400 

    response={}
    response["Message"]="Unknown error occured!"
    return jsonify(response), 500 

@app.route('/asd8734kslsdasldasd09asslkdjasd-lksdj98-lsdsdsad', methods=['GET'])
def deleteAndCleanUpUploadFolder():
    import shutil
    try:
        shutil.rmtree("./uploaded_images/")
    except:
        return jsonify({"message":"Already empty!"}), 200
    return jsonify({"message":"Done!"}), 200

@app.route('/output/<imageFoldername>/<imageFilename>', methods=['GET'])
def getResultantImage(imageFoldername,imageFilename):
    return send_from_directory(UPLOAD_FOLDER+"/"+imageFoldername, imageFilename)


if __name__ == '__main__':
    #COMMENT BELOW LINE WHEN HOSTING THE APP
    app.run(debug=True,host='0.0.0.0')
