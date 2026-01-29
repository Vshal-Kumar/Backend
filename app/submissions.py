from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
import asyncio

from app.db import submissions_col, feedback_col
from app.submission_service import submit_and_evaluate

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.route("", methods=["POST"])
@jwt_required()
def create_submission_api():
    user_id = get_jwt_identity()
    data = request.json or {}

    required = ["internshipId", "taskId", "taskDescription", "submittedData"]
    for r in required:
        if r not in data:
            return jsonify({"error": f"{r} is required"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    submission_id = loop.run_until_complete(
        submit_and_evaluate(user_id, data)
    )

    return jsonify({
        "submissionId": str(submission_id),
        "status": "submitted"
    }), 201


@submissions_bp.route("/<submission_id>", methods=["GET"])
@jwt_required()
def get_submission(submission_id):
    user_id = ObjectId(get_jwt_identity())
    sid = ObjectId(submission_id)

    submission = submissions_col.find_one({
        "_id": sid,
        "userId": user_id
    })

    if not submission:
        return jsonify({"error": "Submission not found"}), 404

    submission["_id"] = str(submission["_id"])
    submission["userId"] = str(submission["userId"])
    submission["internshipId"] = str(submission["internshipId"])
    submission["taskId"] = str(submission["taskId"])

    return jsonify(submission), 200


@submissions_bp.route("/<submission_id>/feedback", methods=["GET"])
@jwt_required()
def get_feedback(submission_id):
    fid = ObjectId(submission_id)

    feedback = feedback_col.find_one({"submissionId": fid})
    if not feedback:
        return jsonify({"error": "Feedback not ready"}), 404

    feedback["_id"] = str(feedback["_id"])
    feedback["submissionId"] = str(feedback["submissionId"])

    return jsonify(feedback), 200


@submissions_bp.route("/tasks/<task_id>/submissions", methods=["GET"])
@jwt_required()
def get_task_submissions(task_id):
    tid = ObjectId(task_id)
    user_id = ObjectId(get_jwt_identity())

    submissions = []
    for s in submissions_col.find({
        "taskId": tid,
        "userId": user_id
    }):
        s["_id"] = str(s["_id"])
        s["taskId"] = str(s["taskId"])
        s["internshipId"] = str(s["internshipId"])
        submissions.append(s)

    return jsonify(submissions), 200
