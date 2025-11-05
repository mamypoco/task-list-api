from flask import Blueprint, request, Response, abort, make_response
from app.models.goal import Goal
from ..db import db
from .route_utilities import validate_model

goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")

@goals_bp.post("")
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

@goals_bp.get("")
def get_all_goals():
    query = db.select(Goal)

    goals = db.session.scalars(query)

    goal_dict = []

    for goal in goals:
        goal_dict.append(
            goal.to_dict()) # reading to dict

    return goal_dict

@goals_bp.get("<goal_id>")
def get_one_goal(goal_id):

    goal = validate_model(Goal, goal_id)

    return goal.to_dict()


@goals_bp.put("<goal_id>")
def update_goal(goal_id):
    goal = validate_model(Goal, goal_id)
    request_body = request.get_json()

    goal.title = request_body["title"]
    
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@goals_bp.delete("<goal_id>")
def delete_model(goal_id):
    goal = validate_model(Goal, goal_id)

    db.session.delete(goal)
    db.session.commit()

    return Response(status=204, mimetype="application/jason")


# def validate_goal(goal_id):
#     try:
#         goal_id = int(goal_id)
    
#     except ValueError:
#         response = {"message": f"goal {goal_id} is invalid"}
#         abort(make_response(response, 400))

#     query = db.select(Goal).where(Goal.id == goal_id)
#     goal = db.session.scalar(query)

#     if not goal:
#         response = {"message": f"goal {goal_id} is not found"}
#         abort(make_response(response, 404))

#     return goal



