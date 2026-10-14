from typing import List
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from duckduckgo_search import DDGS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

PERSIST_DIR = "vectorstore"


vectordb = Chroma(
    persist_directory=PERSIST_DIR,
    embedding_function=embeddings
)

retriever = vectordb.as_retriever(search_kwargs={"k": 5})


# ==========================================================
# PYDANTIC SCHEMAS
# ==========================================================
class RetrievalInput(BaseModel):
    query: str = Field(..., description="User question requiring retrieval")


class WebSearchInput(BaseModel):
    query: str = Field(..., description="Search query for external web search")


# ==========================================================
# RETRIEVAL TOOL
# ==========================================================

@tool(args_schema=RetrievalInput)
def retrieve_documents(query: str) -> str:
    """
    Retrieve relevant university documents from the vector database.
    Use this for university-specific queries such as courses,
    prerequisites, policies, fees, grading, schedules, and faculty.
    """

    docs = retriever.get_relevant_documents(query)

    formatted = []

    for i, doc in enumerate(docs):

        formatted.append(
            f"""
Document {i+1}
Source: {doc.metadata.get('source_file')}
Department: {doc.metadata.get('department')}
Document Type: {doc.metadata.get('document_type')}
Content:
{doc.page_content}
"""
        )

    return "\n\n".join(formatted)


# ==========================================================
# WEB SEARCH TOOL
# ==========================================================



@tool(args_schema=WebSearchInput)
def web_search(query: str) -> str:
    """
    Search the web when vector DB fails.
    """

    results_text = []

    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=3)

        for r in results:
            results_text.append(
                f"""
Title: {r['title']}
Body: {r['body']}
URL: {r['href']}
"""
            )

    return "\n\n".join(results_text)