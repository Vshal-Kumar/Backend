from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import asyncio

from app.internship_service import generate_and_store
from app.db import internships_col, weekly_plans_col, tasks_col

internships_bp = Blueprint("internships", __name__)

ALLOWED_LEVELS = {"beginner", "intermediate", "advanced"}

def to_object_id(value):
    try:
        return ObjectId(value)
    except Exception:
        return None


@internships_bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_internship():
    user_id = get_jwt_identity()
    payload = request.json or {}

    required = ["domain", "title", "durationWeeks", "daysPerWeek", "skills"]
    for r in required:
        if r not in payload:
            return jsonify({"error": f"{r} is required"}), 400

    for s in payload["skills"]:
        if not isinstance(s, list) or len(s) != 2 or s[1] not in ALLOWED_LEVELS:
            return jsonify({
                "error": "skills must be [['skill', 'beginner|intermediate|advanced']]"
            }), 400

    # Flask-safe async execution
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    internship_id, output = loop.run_until_complete(
        generate_and_store(user_id, payload)
    )

    return jsonify({
        "internshipId": str(internship_id),
        "internship": output["internship"],
        "weeklyPlans": output["weekly_plans"],
        "tasks": output["tasks"]
    }), 200


@internships_bp.route("", methods=["GET"])
@jwt_required()
def get_internships():
    user_id = get_jwt_identity()
    uid = ObjectId(user_id)

    internships = []
    for i in internships_col.find({"userId": uid}):
        i["_id"] = str(i["_id"])
        i["userId"] = str(i["userId"])
        internships.append(i)

    return jsonify(internships), 200


@internships_bp.route("/<internship_id>", methods=["GET"])
@jwt_required()
def get_internship(internship_id):
    iid = to_object_id(internship_id)
    if not iid:
        return jsonify({"error": "Invalid internship id"}), 400

    user_id = ObjectId(get_jwt_identity())

    internship = internships_col.find_one({
        "_id": iid,
        "userId": user_id
    })

    if not internship:
        return jsonify({"error": "Internship not found"}), 404

    internship["_id"] = str(internship["_id"])
    internship["userId"] = str(internship["userId"])

    return jsonify(internship), 200



@internships_bp.route("/<internship_id>/weeks", methods=["GET"])
@jwt_required()
def get_weeks(internship_id):
    iid = to_object_id(internship_id)
    if not iid:
        return jsonify({"error": "Invalid internship id"}), 400

    weeks = []
    for w in weekly_plans_col.find({"internshipId": iid}).sort("weekNumber", 1):
        w["_id"] = str(w["_id"])
        w["internshipId"] = str(w["internshipId"])
        weeks.append(w)

    return jsonify(weeks), 200


@internships_bp.route("/<internship_id>/tasks", methods=["GET"])
@jwt_required()
def get_tasks(internship_id):
    iid = to_object_id(internship_id)
    if not iid:
        return jsonify({"error": "Invalid internship id"}), 400

    week_number = request.args.get("week")
    query = {"internshipId": iid}

    if week_number:
        week_doc = weekly_plans_col.find_one({
            "internshipId": iid,
            "weekNumber": int(week_number)
        })
        if not week_doc:
            return jsonify([]), 200
        query["weekId"] = week_doc["_id"]

    tasks = []
    for t in tasks_col.find(query):
        t["_id"] = str(t["_id"])
        t["internshipId"] = str(t["internshipId"])
        t["weekId"] = str(t["weekId"])
        tasks.append(t)

    return jsonify(tasks), 200

@internships_bp.route("/<internship_id>/tasks/<task_id>", methods=["GET"])
@jwt_required()
def get_single_task(internship_id, task_id):
    user_id = ObjectId(get_jwt_identity())

    iid = to_object_id(internship_id)
    tid = to_object_id(task_id)

    if not iid or not tid:
        return jsonify({"error": "Invalid internshipId or taskId"}), 400

    # Ensure internship belongs to user
    internship = internships_col.find_one({
        "_id": iid,
        "userId": user_id
    })
    if not internship:
        return jsonify({"error": "Internship not found"}), 404

    task = tasks_col.find_one({
        "_id": tid,
        "internshipId": iid
    })

    if not task:
        return jsonify({"error": "Task not found"}), 404

    # Serialize ObjectIds
    task["_id"] = str(task["_id"])
    task["internshipId"] = str(task["internshipId"])
    task["weekId"] = str(task["weekId"])

    return jsonify(task), 200
