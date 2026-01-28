import json
from ai.agent import Agent

# Instantiate agent once (singleton-style)
feedback_agent = Agent(
    name="context_aware_code_feedback_agent",
    model="llama-3.3-70b-versatile",
    system_prompt="""
You are an execution-only code evaluation and feedback agent.

CRITICAL RULES (NON-NEGOTIABLE):
- Output MUST be VALID JSON
- Do NOT use markdown
- Do NOT wrap output in ``` or ```json
- Do NOT add explanations
- Do NOT add comments
- Output ONLY a JSON object
- If evaluation cannot be performed, output an EMPTY JSON object: {}

INPUT CONTEXT:
- You will receive:
  1) the task description
  2) the submitted source code
- Evaluate the code strictly against the task description
- Do NOT assume requirements that are not stated in the task

EVALUATION PRINCIPLES:
- Check whether the code fulfills all requirements in the task description
- Evaluate correctness, completeness, structure, readability, and best practices
- Identify missing functionality relative to the task
- Be precise, technical, and actionable

FEEDBACK QUALITY RULES:
- strengths: list concrete parts of the code that correctly satisfy the task
- weaknesses: list specific mismatches, bugs, or missing requirements
- improvements: list exact changes needed to better satisfy the task
- recommendedNextSteps: suggest specific skills or tasks based on gaps found

REQUIRED OUTPUT KEYS:
- strengths
- weaknesses
- improvements
- recommendedNextSteps

FIELD CONSTRAINTS:
- All fields MUST be arrays
- Arrays MUST contain non-empty strings
- No extra keys
- No empty arrays

You ONLY output the final JSON object.
"""
)

async def generate_feedback(payload: dict) -> dict:
    """
    Expected payload:
    {
        "taskDescription": "string",
        "submittedCode": "string"
    }
    """

    prompt = f"""
TASK DESCRIPTION:
{payload.get("taskDescription", "")}

SUBMITTED CODE:
{payload.get("submittedCode", "")}

OUTPUT:
{{
  "strengths": [],
  "weaknesses": [],
  "improvements": [],
  "recommendedNextSteps": []
}}
"""

    raw = await feedback_agent.run(prompt)

    if not raw or not raw.strip():
        raise RuntimeError("AI returned empty response")

    raw = raw.strip()

    # Guard: strip markdown if model disobeys
    if raw.startswith("```"):
        raw = raw.removeprefix("```json")
        raw = raw.removeprefix("```")
        raw = raw.removesuffix("```")
        raw = raw.strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        raise RuntimeError(f"Invalid AI JSON output:\n{raw}")

    # Hard validation to avoid downstream crashes
    required_keys = [
        "strengths",
        "weaknesses",
        "improvements",
        "recommendedNextSteps"
    ]

    for key in required_keys:
        if key not in parsed:
            raise RuntimeError(f"AI output missing required field: {key}")
        if not isinstance(parsed[key], list) or not parsed[key]:
            raise RuntimeError(f"AI output field '{key}' must be a non-empty list")
        for item in parsed[key]:
            if not isinstance(item, str) or not item.strip():
                raise RuntimeError(f"Invalid entry in '{key}'")

    return parsed
