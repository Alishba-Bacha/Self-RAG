import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

DATA_DIR = "Data_share"
PERSIST_DIR = "vectorstore"


def extract_metadata(file_name: str):
    """
    Create meaningful metadata based on document name.
    """

    if "CS" in file_name:
        return {
            "department": "Computer Science",
            "document_type": "course_catalog",
            "level": "undergraduate_graduate"
        }

    elif "EE" in file_name:
        return {
            "department": "Electrical Engineering",
            "document_type": "course_catalog",
            "level": "undergraduate_graduate"
        }

    elif "BBA" in file_name:
        return {
            "department": "Business Administration",
            "document_type": "course_catalog",
            "level": "undergraduate_graduate"
        }

    elif "Policies" in file_name:
        return {
            "department": "University",
            "document_type": "academic_policy",
            "level": "general"
        }

    elif "Faculty" in file_name:
        return {
            "department": "University",
            "document_type": "faculty_directory",
            "level": "general"
        }

    return {
        "department": "Unknown",
        "document_type": "unknown",
        "level": "unknown"
    }


all_docs = []

for pdf_file in os.listdir(DATA_DIR):

    if not pdf_file.endswith(".pdf"):
        continue

    full_path = os.path.join(DATA_DIR, pdf_file)

    loader = PyPDFLoader(full_path)
    docs = loader.load()

    metadata = extract_metadata(pdf_file)

    for doc in docs:
        doc.metadata.update(metadata)
        doc.metadata["source_file"] = pdf_file

    all_docs.extend(docs)


# Structure-aware chunking
# Large chunk size to preserve course descriptions and policies together
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " "]
)

chunks = splitter.split_documents(all_docs)

print(f"Total chunks created: {len(chunks)}")


vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=PERSIST_DIR
)

vectordb.persist()

print("Vector database created successfully.")