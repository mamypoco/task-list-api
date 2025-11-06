from flask import Blueprint, make_response, abort, request, Response
from app.models.task import Task
from ..db import db
from datetime import datetime
import requests
import os
from .route_utilities import validate_model

bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks")

@bp.post("")
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


@bp.get("")
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

    tasks = db.session.scalars(query)

    task_dict = []
    # for task in tasks:
    #     task_dict.append({
    #         task.to_dict()
    #     })

    for task in tasks:
        task_dict.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "is_complete": task.completed_at is not None
        })

    return task_dict

@bp.get("/<task_id>")
def get_one_task(task_id):

    task = validate_model(Task, task_id)

    return task.to_dict()
    
    # return {
    #     "id": task.id,
    #     "title": task.title,
    #     "description": task.description,
    #     "is_complete": task.completed_at is not None
    # }

@bp.put("/<task_id>")
def update_task(task_id):
    task = validate_model(Task, task_id)
    request_body = request.get_json()

    task.title = request_body["title"]
    task.description = request_body["description"]
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.patch("/<task_id>/mark_complete")
def mark_complete_task(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()
    
    db.session.commit()

    # --- send message to slack channel ---
    url = "https://slack.com/api/chat.postMessage"
    data = {
        "text": f"Someone just completed the task {task.title}😺",
        "channel": "test-slack-api"
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"
    }

    requests.post(url, headers=headers, json=data)
    # -----------------------------------
    return Response(status=204, mimetype="application/json")


@bp.patch("/<task_id>/mark_incomplete")
def mark_incomplete_task(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("/<task_id>")
def delete_task(task_id):
    task = validate_model(Task, task_id)

    db.session.delete(task)
    db.session.commit()

    return Response(status=204, mimetype="application/jason")
