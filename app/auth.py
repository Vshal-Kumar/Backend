from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from datetime import datetime
from app.db import users_col

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "email and password required"}), 400

    if users_col.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 409

    user = {
        "email": data["email"],
        "passwordHash": generate_password_hash(data["password"]),
        "authProvider": "local",
        "name": data.get("name"),
        "college": data.get("college"),
        "course": data.get("course"),
        "semester": data.get("semester"),
        "emailVerified": False,
        "onboardingCompleted": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }

    users_col.insert_one(user)

    return jsonify({"message": "User registered"}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "email and password required"}), 400

    user = users_col.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["passwordHash"], data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user["_id"]))

    return jsonify({"accessToken": token}), 200

