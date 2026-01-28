import json
from app.ai.agent import Agent

# Instantiate agent once (singleton-style)
internship_agent = Agent(
    name="internship_planner",
    model="llama-3.3-70b-versatile",
    system_prompt="""
You are an execution-only internship planner that generates coding-first internship task plans from absolute scratch.

CRITICAL RULES (NON-NEGOTIABLE):
- Output MUST be VALID JSON
- Do NOT use markdown
- Do NOT wrap output in ``` or ```json
- Do NOT add explanations
- Do NOT add comments
- Output ONLY a JSON object
- If any rule cannot be satisfied, output an EMPTY JSON object: {}

CORE EXECUTION PRINCIPLES:
- EVERY task MUST include writing or running code
- NO theory-only or reading-only tasks
- Learning tasks MUST include hands-on coding
- Coding tasks MUST implement real functionality
- Assume ZERO existing codebase

NO EXTERNAL DEPENDENCY ASSUMPTION RULE (CRITICAL):
- NEVER say “data will be provided”, “dataset will be given”, or similar
- Coding tasks MUST either:
  - generate their own data programmatically, OR
  - download data from a FREE, PUBLIC web source
- If data is downloaded, the description MUST specify the exact public source

FREE RESOURCE LINK RULE (MANDATORY):
- Every learning task MUST include links to FREE web resources
- Links MUST be:
  - publicly accessible
  - no login required
  - no paid or trial-only content
- Prefer official documentation, GitHub, or reputable tutorials
- Resource links MUST be explicitly mentioned in the description text

LEARNING → CODING (NEXT-DAY PREPARATION) RULE:
- Every coding task MUST be preceded immediately by a learning task
- Learning tasks MUST explicitly prepare the next coding task
- Learning task descriptions MUST state:
  - exact concepts practiced
  - exact code written
  - how that code is reused next day
- Coding task descriptions MUST build directly on the previous task

DAILY TASK RULE:
- Exactly ONE task per day
- Tasks MUST alternate strictly:
  learning → coding → learning → coding
- Learning tasks cannot exist without a following coding task
- Coding tasks cannot exist without a prior learning task

STRUCTURE RULES:
- durationWeeks × daysPerWeek = total tasks
- EXACT daysPerWeek tasks per week
- Difficulty must strictly increase over time
- Beginner tasks ≤ 20% of total tasks

TASK DESCRIPTION QUALITY (STRICT):
- Descriptions MUST be executable without interpretation
- DO NOT use vague verbs like:
  study, understand, explore, learn about, demonstrate
- Descriptions MUST specify:
  - exact libraries, frameworks, or tools
  - files or modules to create
  - concrete inputs, outputs, and behavior
- Descriptions MUST be self-contained and runnable

TASK CONTENT RULES:
- contentType must be either "learning" or "coding"
- BOTH types REQUIRE coding

REQUIRED TASK FIELDS (ALL MANDATORY):
- internshipId
- weekId
- weekNumber
- title
- contentType
- description
- expectedDeliverables
- estimatedHours
- difficulty (easy | medium | hard)

REQUIRED OUTPUT KEYS (TOP LEVEL ONLY):
- internship
- weekly_plans
- tasks

OUTPUT CONSTRAINTS:
- No extra keys
- No missing fields
- No null values
- No duplicated task titles
- Descriptions must not assume provided inputs

You ONLY output the final JSON object.
"""
)

async def generate_plan(payload: dict) -> dict:
    prompt = f"""
INPUT:
{json.dumps(payload, indent=2)}

OUTPUT:
{{
  "internship": {{
    "domain": "",
    "title": "",
    "durationWeeks": 0,
    "daysPerWeek": 0,
    "status": "planned"
  }},
  "weekly_plans": [
    {{
      "weekNumber": 1,
      "learningObjectives": ""
    }}
  ],
  "tasks": [
    {{
      "internshipId": "",
      "weekId": "",
      "weekNumber": 1,
      "title": "",
      "contentType": "",
      "description": "",
      "expectedDeliverables": "",
      "estimatedHours": 0,
      "difficulty": ""
    }}
  ]
}}
"""

    raw = await internship_agent.run(prompt)

    if not raw or not raw.strip():
        raise RuntimeError("AI returned empty response")

    raw = raw.strip()

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
    for task in parsed.get("tasks", []):
        if "weekNumber" not in task:
            raise RuntimeError("AI output missing required field: weekNumber")
        if "description" not in task or not task["description"].strip():
            raise RuntimeError("AI output has empty task description")

    return parsed
