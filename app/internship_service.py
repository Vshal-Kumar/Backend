from bson import ObjectId
from app.ai.generate import generate_plan
from app.db import internships_col, weekly_plans_col, tasks_col
from datetime import datetime

async def generate_and_store(user_id, payload):
    ai_output = await generate_plan(payload)

    internship_id = internships_col.insert_one({
        "userId": ObjectId(user_id),
        **ai_output["internship"],
        "createdAt": datetime.utcnow()
    }).inserted_id

    week_id_map = {}

    for w in ai_output["weekly_plans"]:
        res = weekly_plans_col.insert_one({
            "internshipId": internship_id,
            "weekNumber": w["weekNumber"],
            "learningObjectives": w["learningObjectives"],
            "createdAt": datetime.utcnow()
        })
        week_id_map[w["weekNumber"]] = res.inserted_id

    for t in ai_output["tasks"]:
        tasks_col.insert_one({
            "internshipId": internship_id,
            "weekId": week_id_map[t["weekNumber"]],
            "title": t["title"],
            "contentType": t["contentType"],
            "description": t["description"],
            "expectedDeliverables": t["expectedDeliverables"],
            "estimatedHours": t["estimatedHours"],
            "difficulty": t["difficulty"],
            "createdAt": datetime.utcnow()
        })

    return internship_id, ai_output
