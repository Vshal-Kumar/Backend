from dotenv import load_dotenv
import os
import httpx

load_dotenv()


class Agent:
    """
    Generic async LLM agent.
    Responsible ONLY for:
    - sending prompts
    - returning raw text output

    It does NOT:
    - parse JSON
    - touch DB
    - modify responses
    """

    def __init__(self, name: str, model: str, system_prompt: str):
        self.name = name
        self.model = model
        self.system_prompt = system_prompt

        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL")

        if not self.api_key:
            raise RuntimeError("LLM_API_KEY not set in environment")

        if not self.base_url:
            raise RuntimeError("LLM_BASE_URL not set in environment")

    async def run(self, user_prompt: str) -> str:
        """
        Sends prompt to the LLM and returns RAW response text.
        Caller is responsible for parsing / validation.
        """

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.system_prompt.strip()
                },
                {
                    "role": "user",
                    "content": user_prompt.strip()
                }
            ],
            # Low temperature = deterministic JSON
            "temperature": 0.2
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                self.base_url, # type: ignore
                json=payload,
                headers=headers
            )

        if response.status_code != 200:
            raise RuntimeError(
                f"LLM request failed "
                f"(status={response.status_code}): {response.text}"
            )

        data = response.json()

        # OpenAI / Groq compatible response format
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError):
            raise RuntimeError(f"Unexpected LLM response format: {data}")
