from flask import Blueprint, make_response, abort, request
from app.models.task import Task
from ..db import db

tasks_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")

@tasks_bp.post()
def create_task():
    request_body = request.get_json()
    title = request_body["title"]
    description = request_body["description"]
    
    new_task = Task(title=title, description=description)
    db.session.add(new_task)
    db.session.commit()

    response = {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description
    }
    return response, 201

@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task).order_by(Task.id)
    tasks = db.session.scalars(query)

    result_list = []

    for task in tasks:
        result_list.append({
            "id": task.id,
            "title": task.title,
            "description": task.description
        })
    return result_list



