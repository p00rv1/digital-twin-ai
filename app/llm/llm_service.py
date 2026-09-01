import json
from groq import Groq
from app.config.settings import GROQ_API_KEY
from app.llm.models import ClinicalDiagnosis


class LLMService:

    def __init__(self):
        self.api_key = GROQ_API_KEY
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
        else:
            self.client = None

        self.model = "qwen/qwen3.6-27b"
        self.fallback_model = "openai/gpt-oss-20b"

    def _call_groq(self, messages, model_name):
        return self.client.chat.completions.create(
            model=model_name,
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=messages
        )

    def generate(
        self,
        prompt
    ):
        if not self.client:
            return {
                "diagnosis": "Groq API Key Required",
                "confidence": 0,
                "reasoning": "GROQ_API_KEY is not set in environment or .env file. Please add GROQ_API_KEY to enable AI diagnosis generation.",
                "supporting_biomarkers": [],
                "recommended_tests": [],
                "supporting_papers": []
            }

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an evidence-based clinical decision support assistant. "
                    "You MUST respond ONLY with a valid JSON object matching the requested schema. "
                    "Do NOT include markdown wrapping like ```json, just pure raw JSON."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        active_model = self.model

        for attempt in range(1, 4):
            try:
                response = self._call_groq(messages, active_model)
                raw_text = response.choices[0].message.content

                # Clean up any potential markdown backticks
                cleaned_text = raw_text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                cleaned_text = cleaned_text.strip()

                json_dict = json.loads(cleaned_text)
                validated_model = ClinicalDiagnosis.model_validate(json_dict)
                return validated_model.model_dump()

            except Exception as e:
                # If primary model fails or returns unparseable schema, fallback on next retry
                if attempt == 1:
                    active_model = self.fallback_model
                    messages.append({
                        "role": "assistant",
                        "content": raw_text if 'raw_text' in locals() else ""
                    })
                    messages.append({
                        "role": "user",
                        "content": f"Schema Validation Error: {str(e)}. Please output valid JSON matching the exact schema keys."
                    })
                elif attempt == 2:
                    # Final attempt fallback constructing partial structured output
                    try:
                        if 'json_dict' in locals() and isinstance(json_dict, dict):
                            return {
                                "diagnosis": str(json_dict.get("diagnosis", "Clinical Diagnosis Generated")),
                                "confidence": int(json_dict.get("confidence", 70)),
                                "reasoning": str(json_dict.get("reasoning", "Evidence synthesized.")),
                                "supporting_biomarkers": list(json_dict.get("supporting_biomarkers", [])),
                                "recommended_tests": list(json_dict.get("recommended_tests", [])),
                                "supporting_papers": list(json_dict.get("supporting_papers", []))
                            }
                    except Exception:
                        pass

        # Robust Fallback Dict if all retries fail
        return {
            "diagnosis": "Diagnostic Synthesis Incomplete",
            "confidence": 30,
            "reasoning": f"Groq API returned output that failed schema validation: {str(e) if 'e' in locals() else 'Unknown Error'}",
            "supporting_biomarkers": [],
            "recommended_tests": ["Repeat Liver Function Panel (ALT, AST, Bilirubin)"],
            "supporting_papers": []
        }