import time
import json
from groq import Groq
from app.config.settings import GROQ_API_KEY


class LLMService:

    def __init__(self):
        self.api_key = GROQ_API_KEY
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Groq init warning: {e}")
                self.client = None
        else:
            self.client = None

        self.model = "llama-3.3-70b-versatile"

    def generate(
        self,
        prompt,
        max_retries=3
    ):
        if not self.client:
            return {
                "diagnosis": "Clinical AI Service Offline (Groq API Key missing or invalid)",
                "confidence": 0.0,
                "reasoning": "Please configure a valid GROQ_API_KEY in .env file to enable live diagnostic generation."
            }

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.2,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an evidence-based medical AI assistant. "
                                "Provide structured, literature-backed analysis. "
                                "Respond in JSON format with keys: 'diagnosis', 'confidence', 'summary', and 'recommendations'."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                content = response.choices[0].message.content.strip()
                try:
                    # Attempt to parse JSON if returned as string
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:].strip()
                    return json.loads(content)
                except Exception:
                    return content

            except Exception as e:
                print(f"LLM API Call Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    return {
                        "error": str(e),
                        "diagnosis": "Diagnostic pipeline encountered an LLM provider error.",
                        "confidence": 0.0
                    }
                time.sleep(2 ** attempt)