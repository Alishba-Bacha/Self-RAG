
from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

from tools import retrieve_documents, web_search
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3",
    temperature=0
)


# ==========================================================
# GRAPH STATE
# ==========================================================

class GraphState(TypedDict):

    question: str

    needs_retrieval: bool
    retrieval_reason: str

    retrieved_docs: str

    relevant_docs: str

    use_web_search: bool

    generated_answer: str

    hallucination_detected: bool

    retry_count: int

    trace: List[str]


# ==========================================================
# NODE 1: RETRIEVAL DECISION
# ==========================================================


def decide_retrieval(state: GraphState):

    question = state["question"]

    prompt = ChatPromptTemplate.from_template(
        """
You are a routing classifier.

Determine whether the user query requires retrieval from a university knowledge base.

Retrieval is REQUIRED for:
- courses
- prerequisites
- faculty
- fees
- attendance
- GPA policies
- schedules
- semester rules
- university-specific information

Retrieval is NOT required for:
- greetings
- casual conversation
- generic knowledge
- simple definitions

Return ONLY this format:

NEEDS_RETRIEVAL: YES or NO
REASON: explanation

Query:
{question}
"""
    )

    chain = prompt | llm

    response = chain.invoke({"question": question}).content

    needs = "YES" in response.upper()

    trace = state.get("trace", [])

    trace.append(f"[Retrieval Decision] {response}")

    return {
        **state,
        "needs_retrieval": needs,
        "retrieval_reason": response,
        "trace": trace
    }


# ==========================================================
# NODE 2: DIRECT ANSWER
# ==========================================================


def direct_answer(state: GraphState):

    question = state["question"]

    response = llm.invoke(question).content

    trace = state["trace"]
    trace.append("[Direct Answer] Retrieval skipped.")

    return {
        **state,
        "generated_answer": response,
        "trace": trace
    }


# ==========================================================
# NODE 3: RETRIEVE DOCUMENTS
# ==========================================================


def retrieve(state: GraphState):

    question = state["question"]

    docs = retrieve_documents.invoke({"query": question})

    trace = state["trace"]
    trace.append("[Retrieve] Documents fetched from vector DB.")

    return {
        **state,
        "retrieved_docs": docs,
        "trace": trace
    }


# ==========================================================
# NODE 4: RELEVANCE GRADING
# ==========================================================


def grade_relevance(state: GraphState):

    question = state["question"]
    docs = state["retrieved_docs"]

    split_docs = docs.split("Document ")

    relevant_docs = []

    trace = state["trace"]

    for doc in split_docs:

        if not doc.strip():
            continue

        prompt = ChatPromptTemplate.from_template(
            """
You are a relevance grader.

Determine if the following document is relevant to the user query.

Return ONLY:
RELEVANT
or
IRRELEVANT

Question:
{question}

Document:
{document}
"""
        )

        chain = prompt | llm

        result = chain.invoke(
            {
                "question": question,
                "document": doc
            }
        ).content.strip()

        trace.append(f"[Relevance Grading] {result}")

        if "RELEVANT" in result:
            relevant_docs.append(doc)

    if len(relevant_docs) == 0:

        trace.append("[Relevance] No relevant documents found.")

        return {
            **state,
            "relevant_docs": "",
            "use_web_search": True,
            "trace": trace
        }

    return {
        **state,
        "relevant_docs": "\n\n".join(relevant_docs),
        "use_web_search": False,
        "trace": trace
    }


# ==========================================================
# NODE 5: WEB SEARCH FALLBACK
# ==========================================================


def search_web(state: GraphState):

    question = state["question"]

    results = web_search.invoke({"query": question})

    trace = state["trace"]

    trace.append("[Web Search] External web search triggered.")

    return {
        **state,
        "relevant_docs": results,
        "trace": trace
    }


# ==========================================================
# NODE 6: GENERATION
# ==========================================================


def generate_answer(state: GraphState):

    question = state["question"]
    context = state["relevant_docs"]

    prompt = ChatPromptTemplate.from_template(
        """
You are a university advisory assistant.

Answer ONLY using the provided context.

If the information is not present in the context,
clearly say that you do not know.

Context:
{context}

Question:
{question}
"""
    )

    chain = prompt | llm

    answer = chain.invoke(
        {
            "context": context,
            "question": question
        }
    ).content

    trace = state["trace"]

    trace.append("[Generation] Response generated.")

    return {
        **state,
        "generated_answer": answer,
        "trace": trace
    }


# ==========================================================
# NODE 7: HALLUCINATION CHECK
# ==========================================================


def hallucination_check(state: GraphState):

    answer = state["generated_answer"]
    context = state["relevant_docs"]

    prompt = ChatPromptTemplate.from_template(
        """
You are a hallucination detector.

Determine whether the answer contains claims not supported
by the provided context.

Return ONLY:
SUPPORTED
or
HALLUCINATED

Context:
{context}

Answer:
{answer}
"""
    )

    chain = prompt | llm

    result = chain.invoke(
        {
            "context": context,
            "answer": answer
        }
    ).content.strip()

    trace = state["trace"]

    trace.append(f"[Hallucination Check] {result}")

    hallucinated = "HALLUCINATED" in result

    return {
        **state,
        "hallucination_detected": hallucinated,
        "trace": trace
    }


# ==========================================================
# NODE 8: RETRY OR DISCLAIMER
# ==========================================================


def retry_or_finalize(state: GraphState):

    retries = state.get("retry_count", 0)

    trace = state["trace"]

    if state["hallucination_detected"]:

        if retries < 2:

            trace.append(f"[Retry] Regenerating answer. Attempt {retries + 1}")

            return {
                **state,
                "retry_count": retries + 1,
                "trace": trace
            }

        else:

            trace.append("[Failure] Retry limit exceeded.")

            return {
                **state,
                "generated_answer": (
                    "I could not fully verify the requested information "
                    "from the available evidence."
                ),
                "trace": trace
            }

    trace.append("[Success] Answer verified.")

    return state


# ==========================================================
# ROUTING FUNCTIONS
# ==========================================================


def route_retrieval(state: GraphState):

    if state["needs_retrieval"]:
        return "retrieve"

    return "direct_answer"



def route_web_search(state: GraphState):

    if state["use_web_search"]:
        return "web_search"

    return "generate"



def route_hallucination(state: GraphState):

    if state["hallucination_detected"] and state["retry_count"] < 2:
        return "generate"

    return END


# ==========================================================
# BUILD GRAPH
# ==========================================================

workflow = StateGraph(GraphState)

workflow.add_node("decide_retrieval", decide_retrieval)
workflow.add_node("direct_answer", direct_answer)
workflow.add_node("retrieve", retrieve)
workflow.add_node("grade_relevance", grade_relevance)
workflow.add_node("web_search", search_web)
workflow.add_node("generate", generate_answer)
workflow.add_node("hallucination_check", hallucination_check)
workflow.add_node("retry_or_finalize", retry_or_finalize)

workflow.set_entry_point("decide_retrieval")

workflow.add_conditional_edges(
    "decide_retrieval",
    route_retrieval,
    {
        "retrieve": "retrieve",
        "direct_answer": "direct_answer"
    }
)

workflow.add_edge("retrieve", "grade_relevance")

workflow.add_conditional_edges(
    "grade_relevance",
    route_web_search,
    {
        "web_search": "web_search",
        "generate": "generate"
    }
)

workflow.add_edge("web_search", "generate")
workflow.add_edge("generate", "hallucination_check")
workflow.add_edge("hallucination_check", "retry_or_finalize")

workflow.add_conditional_edges(
    "retry_or_finalize",
    route_hallucination,
    {
        "generate": "generate",
        END: END
    }
)

workflow.add_edge("direct_answer", END)

app = workflow.compile()