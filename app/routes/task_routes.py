from flask import Blueprint, make_response, abort, request, Response
from app.models.task import Task
from ..db import db
from datetime import datetime
import requests
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@tasks_bp.post("")
def create_task():
    request_body = request.get_json()

    try: 
        new_task = Task.from_dict(request_body)

    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400)) 
    
    db.session.add(new_task)
    db.session.commit()

    response = {
        "id": new_task.id,
        "title": new_task.title,
        "description": new_task.description,
        "is_complete": new_task.completed_at is not None
    }
    return response, 201


@tasks_bp.get("")
def get_all_tasks():
    query = db.select(Task)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(Task.title.ilike(f"%{title_param}%"))
    
    # else:
    sort_order = request.args.get("sort", "asc")

    if sort_order == "desc":
        query = query.order_by(Task.title.desc())
    else:
        query = query.order_by(Task.title.asc())
            # query = query.order_by(Task.title)

    tasks = db.session.scalars(query)

    task_dict = []

    for task in tasks:
        task_dict.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        })

    return task_dict

@tasks_bp.get("/<task_id>")
def get_one_task(task_id):

    task = validate_task(task_id)
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "is_complete": task.completed_at is not None
    }

@tasks_bp.put("/<task_id>")
def update_task(task_id):
    task = validate_task(task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_complete")
def mark_complete_task(task_id):
    task = validate_task(task_id)

    task.completed_at = datetime.now()
    
    db.session.commit()

    url = "https://slack.com/api/chat.postMessage"

    data = {
        "text": "Someone just completed the task My Beautiful Task😺",
        "channel": "test-slack-api"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }

    requests.post(url, headers=headers, json=data)

    return Response(status=204, mimetype="application/json")


@tasks_bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete_task(task_id):
    task = validate_task(task_id)

    task.completed_at = None
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@tasks_bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_task(task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/jason")


def validate_task(task_id):
    try:
        task_id = int(task_id)

    except ValueError:
        response = {"message": f"task {task_id} is invalid"}
        abort(make_response(response, 400))
    
    query = db.select(Task).where(Task.id == task_id)
    task = db.session.scalar(query)

    if not task:
        response= {"message": f"task {task_id} is not found"}
        abort(make_response(response, 404))

    return task
