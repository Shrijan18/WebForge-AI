# from langchain_groq import ChatGroq

# from app.config.config import settings


# class LLMTool:

#     def __init__(self):

#         self.llm = ChatGroq(
#             model=settings.GROQ_MODEL,
#             api_key=settings.GROQ_API_KEY,
#             temperature=0,
#             max_tokens=2800
#         )

#     def invoke(self, messages, **kwargs):

#         return self.llm.invoke(
#             messages,
#             **kwargs
#         )


from langchain_groq import ChatGroq

from app.config.config import settings


class LLMTool:

    def __init__(self):

        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            api_key=settings.GROQ_API_KEY,
            temperature=0,
            max_completion_tokens=8192,
            reasoning_effort="low"
        )

    def invoke(self, messages, **kwargs):

        return self.llm.invoke(
            messages,
            **kwargs
        )