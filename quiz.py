"""
a quiz feature:
experimental
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
import random
load_dotenv()
#quiz history:
previous_quizzes = []
#llm for quiz
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7
)
# quiz prompt:
quiz_prompt = ChatPromptTemplate.from_template("""
You are a quiz generator for an educational AI assistant.

The assistant previously answered the user's question with an explanation, a real-world scenario, and code.

Your task is to create ONE multiple-choice quiz question to test whether the learner understood the concept.

User Question:
{question}

AI Answer:
{ai_answer}
Previously generated quiz questions:
{previous_questions}
Do not generate a question that is identical or very similar to any of these.

Guidelines:
- Avoid repeating previously generated quiz questions.
- If similar questions already exist, generate a different angle or scenario.
- The quiz must test conceptual understanding rather than memorization.
- Use the explanation and scenario as the main sources for generating the question.
- Sometimes consider the user's original question to guide the quiz focus.
- Do not generate questions that simply repeat the documentation.
- Provide exactly four options.
- Only one option should be correct.
- The incorrect options should represent realistic misunderstandings that a learner might have about the concept.
- The incorrect options should still sound reasonable to encourage thinking.
- The incorrect options should represent realistic misunderstandings that a learner might have about the concept.
- All answer options must be unique.
- No two options should be identical or nearly identical in wording.
- Options may represent closely related ideas, but they must still be clearly distinguishable from each other.

Return the output strictly in JSON format:

{{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_index": 0
}}
""")

#setting parser for structuring the response
parser = JsonOutputParser()
#llm prompt +parser chain:
quiz_chain = quiz_prompt | llm | parser

#function to generate the quiz:

def generate_quiz(question: str, ai_answer: str):

    previous = "\n".join(previous_quizzes)
    result = quiz_chain.invoke({
        "question": question,
        "ai_answer": ai_answer,
        "previous_questions": previous
    })

    previous_quizzes.append(result["question"])
    options = result["options"]
    correct_answer = options[result["correct_index"]]

    # shuffle options
    random.shuffle(options)

    # find new index of correct answer
    new_index = options.index(correct_answer)

    result["options"] = options
    result["correct_index"] = new_index

    return result
