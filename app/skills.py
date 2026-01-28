from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson.objectid import ObjectId
from datetime import datetime
from app.db import user_skills_col

skills_bp = Blueprint("skills", __name__)


@skills_bp.route("/skills", methods=["POST"])
@jwt_required()
def add_skill():
    user_id = get_jwt_identity()
    data = request.json

    if not data or "skill" not in data or "level" not in data:
        return jsonify({"error": "skill and level required"}), 400

    doc = {
        "userId": ObjectId(user_id),
        "skill": data["skill"],
        "level": data["level"],
        "verified": False,
        "createdAt": datetime.utcnow()
    }

    result = user_skills_col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    doc["userId"] = user_id

    return jsonify(doc), 201


@skills_bp.route("/skills", methods=["GET"])
@jwt_required()
def get_skills():
    user_id = get_jwt_identity()

    skills = []
    for s in user_skills_col.find({"userId": ObjectId(user_id)}):
        s["_id"] = str(s["_id"])
        s["userId"] = user_id
        skills.append(s)

    return jsonify(skills), 200


@skills_bp.route("/skills/<skill_id>", methods=["DELETE"])
@jwt_required()
def delete_skill(skill_id):
    user_id = get_jwt_identity()

    result = user_skills_col.delete_one({
        "_id": ObjectId(skill_id),
        "userId": ObjectId(user_id)
    })

    if result.deleted_count == 0:
        return jsonify({"error": "Skill not found"}), 404

    return jsonify({"message": "Skill removed"}), 200
