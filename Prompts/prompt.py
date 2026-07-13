from langchain_core.prompts import PromptTemplate

prompt = PromptTemplate(
    template = """
        You are a very helful assistant.
        Answer only from the provided transcript context of the YT Video.
        If you don't know the answer, say "I don't know".
        Don't answer irrelevant responses.

        This is the context-\n\n
        {context}\n
        Question: {question}\n
    """,
    input_variables=['context', 'question'],
)

