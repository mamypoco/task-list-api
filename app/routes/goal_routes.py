from flask import Blueprint, request, Response, abort, make_response
from app.models.goal import Goal
from app.models.task import Task
from ..db import db
from .route_utilities import validate_model, create_model

bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@bp.post("")
def create_goal():
    request_body = request.get_json()

    try: 
        new_goal = Goal.from_dict(request_body) # creating from dict

    except KeyError:
        response = {"details": "Invalid data"}
        abort(make_response(response, 400))    
    
    db.session.add(new_goal)
    db.session.commit()

    response = {
        "id": new_goal.id,
        "title": new_goal.title    
    }

    return response, 201

@bp.post("/<goal_id>/tasks")
def create_task_with_goal(goal_id):
    
    goal = validate_model(Goal, goal_id)
    # postman request_body = { "task_ids": [1,2,3]}
    request_body = request.get_json() 
    task_ids = request_body["task_ids"] # [1,2,3]

    task_list = [] # [{ }, { }. { }]
    for id in task_ids: # [1,2,3]
        # id 1のタスクを持ってくる
        task = validate_model(Task, id)
        task_list.append(task)

    goal.tasks = task_list
    db.session.commit()

    # taskのIDを元に、task のobjectを持ってきて、リストの中に入れる [1,2,3]
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
    query = db.select(Goal)

    goals = db.session.scalars(query)

    goal_dict = []
    for goal in goals:
        goal_dict.append(
            goal.to_dict()) # reading to dict

    return goal_dict

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


