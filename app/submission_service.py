from bson import ObjectId
from datetime import datetime

from app.db import submissions_col, feedback_col
from app.ai.feedback import generate_feedback


async def submit_and_evaluate(user_id, payload):
    submission = {
        "userId": ObjectId(user_id),
        "internshipId": ObjectId(payload["internshipId"]),
        "taskId": ObjectId(payload["taskId"]),
        "submittedData": payload["submittedData"],
        "status": "submitted",
        "submittedAt": datetime.utcnow()
    }

    submission_res = submissions_col.insert_one(submission)
    submission_id = submission_res.inserted_id

    feedback = await generate_feedback({
        "taskDescription": payload["taskDescription"],
        "submittedCode": payload["submittedData"]
    })

    feedback_col.insert_one({
        "submissionId": submission_id,
        "strengths": feedback["strengths"],
        "weaknesses": feedback["weaknesses"],
        "improvements": feedback["improvements"],
        "recommendedNextSteps": feedback["recommendedNextSteps"],
        "createdAt": datetime.utcnow()
    })

    return submission_id
