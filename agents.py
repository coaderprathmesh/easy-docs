from ingest_data import db_path, collection
#importing packages for similarity search and llm
import os
from pathlib import Path

from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_community.vectorstores import Chroma

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import StateGraph, END
from typing import TypedDict
#importing tools for web search
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from dotenv import load_dotenv

#loading the API keys
load_dotenv()

#declaring the state for the graph (the data that it is going to generate)

class GraphState(TypedDict):
    question: str
    context: str
    sources: list[str]
    explanation: str
    scenario: str
    code: str
    full_answer: str

#declaring the imbeddings and vector db's configgeration
embeddings = OpenAIEmbeddings()
vectordb = Chroma(
    collection_name=collection,
    persist_directory=db_path,
    embedding_function=embeddings
)

#setting up the configgeration for retrever

retriever = vectordb.as_retriever(search_kwargs={"k": 4}) # 4 results will be returned after simlarity search

#first node to fetch context out of provided documentation

def retrieve_context(state):

    question = state["question"]
    #performing the process of similairty search.
    docs = retriever.invoke(question)
    #converting in to string for the context
    context = "\n\n".join(doc.page_content     for doc in docs)
    #preserving the sources (the metadata)
    sources = [doc.metadata.get("source", "unknown") for doc in docs]
    #returns the value of context to update in state.
    return {
        "context": context,
        "sources": sources
    }

#defining the llm model
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
)

#first agent: explaination agent.
#it will explain the answer with the provided context and user question.
def explanation_agent(state):

    question = state["question"]
    context = state["context"]

    prompt = ChatPromptTemplate.from_template(
    """
        You are a senior software educator.

        Your job is to explain technical concepts clearly and simply using the provided documentation context.

        Guidelines:
        - Focus on understanding the concept.
        - Avoid writing code.
        - Use simple language.
        - Base the explanation on the context.

        Context:
        {context}

        Question:
        {question}

        Explain the concept clearly.
    """
    )

    chain = prompt | llm | StrOutputParser()

    explanation = chain.invoke({
        "question": question,
        "context": context
    })
    #returns the explaination
    return {
        "explanation": explanation
    }

#second agent: scenario agent: produces relevant scenarios to make the reader understand concept with greatter accuracy

def scenario_agent(state):

    question = state["question"]
    explanation = state["explanation"]

    prompt = ChatPromptTemplate.from_template(
        """
You are a technical instructor who explains concepts using real-world scenarios.

Using the explanation provided, create a practical real-world example
that helps someone understand the concept intuitively.

Guidelines:
- Use simple language
- Do not repeat the explanation
- Focus on an everyday analogy or real system

Question:
{question}

Explanation:
{explanation}

Provide a real-world scenario that helps understand the concept.
"""
    )

    chain = prompt | llm | StrOutputParser()

    scenario = chain.invoke({
        "question": question,
        "explanation": explanation
    })

    return {
        "scenario": scenario
    }

#defining third agent: code agent.

#declaring the web search tool:

@tool
def web_search(query: str) -> str:
    """
    Search the internet for updated information or code examples.
    Use this tool when documentation context is insufficient
    or when modern coding practices are needed.
    """
    search = DuckDuckGoSearchRun()
    return search.run(query)

#defining the logic of the third agent:

def code_agent(state):

    question = state["question"]
    explanation = state["explanation"]
    scenario = state["scenario"]

    llm_with_tools = llm.bind_tools([web_search])

    prompt = ChatPromptTemplate.from_template(
        """
You are a senior software engineer.

Your task is to generate practical working code.

You have access to a web_search tool that can be used
to fetch modern examples or updated coding practices.

Guidelines:
- Prefer using the explanation first
- Use web_search only if the explanation is not enough
- Produce clear and runnable code

Question:
{question}

Explanation:
{explanation}

Scenario:
{scenario}

Additional context from web search (latest information if requested):
{tool_result}

If this section is empty and you need updated information,
you may call the web_search tool.

Generate the code solution.
"""
    )

    chain = prompt | llm_with_tools

    response = chain.invoke({
        "question": question,
        "explanation": explanation,
        "scenario": scenario,
        "tool_result": ""
    })

    # Detect tool call
    if hasattr(response, "tool_calls") and response.tool_calls:

        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "web_search":
            tool_result = web_search.invoke(tool_args["query"])

            final_chain = prompt | llm | StrOutputParser()

            code = final_chain.invoke({
                "question": question,
                "explanation": explanation,
                "scenario": scenario,
                "tool_result": tool_result
            })

        else:
            code = response.content

    else:
        code = response.content

    return {"code": code}

#final node: combining everything togather

def final_answer_node(state):

    explanation = state["explanation"]
    scenario = state["scenario"]
    code = state["code"]

    sources = state["sources"]

    sources_text = "\n".join(set(sources))
    full_answer = f"""
Explanation
-----------
{explanation}

Real World Scenario
-------------------
{scenario}

Code Example
------------
{code}

Sources
-------
{sources_text}
"""

    return {"full_answer": full_answer}

#lang graf setup
#setting instance of the graph with the class state (graphState)
builder = StateGraph(GraphState)
#adding functions (nodes)

builder.add_node("retrieve", retrieve_context)
builder.add_node("explain", explanation_agent)
builder.add_node("scenario", scenario_agent)
builder.add_node("code", code_agent)
builder.add_node("final", final_answer_node)
#setting the start point of the flow
builder.set_entry_point("retrieve")

#declaring the flow of the graph

builder.add_edge("retrieve", "explain")
builder.add_edge("explain", "scenario")
builder.add_edge("scenario", "code")
builder.add_edge("code", "final")
builder.add_edge("final", END)

#compiles the flow

graph = builder.compile()










