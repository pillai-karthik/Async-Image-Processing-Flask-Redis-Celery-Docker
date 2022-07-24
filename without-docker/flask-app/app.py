from flask import Flask
from celery import Celery

app = Flask(__name__)
simple_app = Celery('simple_worker', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@app.route('/simple_start_task')
def call_method():
    app.logger.info("Invoking Method ")
    #                        queue name in task folder.function name
    r = simple_app.send_task('tasks.longtime_add', kwargs={'x': 1, 'y': 2})
    app.logger.info(r.backend)
    return r.id


@app.route('/task-result/<task_id>')
def get_task_result(task_id):
    status = simple_app.AsyncResult(task_id, app=simple_app)

    if str(status.state)=="SUCCESS":
        result = simple_app.AsyncResult(task_id).result
        
        return jsonify(result), 200

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

#===================OPTIONAL APIs====================
@app.route('/simple_task_status/<task_id>')
def get_status(task_id):
    status = simple_app.AsyncResult(task_id, app=simple_app)
    print("Invoking Method ")
    return "Status of the Task " + str(status.state)


@app.route('/simple_task_result/<task_id>')
def task_result(task_id):
    result = simple_app.AsyncResult(task_id).result
    return "Result of the Task " + str(result)
#====================================================