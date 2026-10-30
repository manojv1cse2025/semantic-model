from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.intent.models import UserIntent


class IntentClassifier:

    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model=settings.model_name,
            google_api_key=settings.google_api_key,
            temperature=0
        )

    async def classify(
        self,
        question: str
    ) -> UserIntent:

        structured_llm = self.llm.with_structured_output(
            UserIntent
        )

        prompt = f"""
You are a semantic analytics intent classifier.

User question:

{question}

Determine:

1. intent
2. metrics
3. dimensions
4. entities
5. filters
6. time range
7. time grain
8. confidence

Do not invent metrics or dimensions.
"""

        return await structured_llm.ainvoke(prompt)
