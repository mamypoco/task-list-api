from flask import Blueprint, request, Response
from app.models.goal import Goal
from app.models.task import Task
from ..db import db
from .route_utilities import validate_model, create_model, get_models_with_filters

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    return create_model(Goal, request_body)

@bp.post("/<goal_id>/tasks")
def create_task_with_goal(goal_id):
    
    goal = validate_model(Goal, goal_id)
    
    request_body = request.get_json() 
    task_ids = request_body["task_ids"] 

    task_list = [] 
    for id in task_ids: 
        task = validate_model(Task, id)
        task_list.append(task)

    goal.tasks = task_list
    db.session.commit()

    return { 
            "id": goal.id,
            "task_ids": task_ids
        }, 200


@bp.get("/<goal_id>/tasks")
def get_tasks_by_goal(goal_id):

    goal = validate_model(Goal, goal_id)
    tasks = [task.to_dict() for task in goal.tasks]

    return {
        "id": goal.id,
        "title": goal.title,
        "tasks": tasks
    }, 200


@bp.get("")
def get_all_goals():

    return get_models_with_filters(Goal, request.args)

@bp.get("<goal_id>")
def get_one_goal(goal_id):

    goal = validate_model(Goal, goal_id)
    return goal.to_dict()


@bp.put("<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("<goal_id>")
def delete_model(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/jason")


