from groq import Groq

from app.config.settings import GROQ_API_KEY


class LLMService:

    def __init__(self):

        self.client = Groq(
            api_key=GROQ_API_KEY
        )

        self.model = "llama-3.3-70b-versatile"
    def generate(
        self,
        prompt
    ):

        response = self.client.chat.completions.create(

            model=self.model,

            temperature=0.2,

            messages=[

                {

                    "role":"system",

                    "content":
                    "You are an evidence-based medical assistant. Use only the supplied evidence."

                },

                {

                    "role":"user",

                    "content":prompt

                }

            ]

        )

        return response.choices[0].message.content