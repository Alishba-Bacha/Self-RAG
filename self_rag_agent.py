
from dotenv import load_dotenv
from graph import app

load_dotenv()


print("=" * 70)
print("SELF-RAG UNIVERSITY COURSE ADVISORY AGENT")
print("=" * 70)


while True:

    query = input("\nStudent Query: ")

    if query.lower() in ["exit", "quit"]:
        break

    result = app.invoke(
        {
            "question": query,
            "needs_retrieval": False,
            "retrieval_reason": "",
            "retrieved_docs": "",
            "relevant_docs": "",
            "use_web_search": False,
            "generated_answer": "",
            "hallucination_detected": False,
            "retry_count": 0,
            "trace": []
        }
    )

    print("\n" + "=" * 70)
    print("EXECUTION TRACE")
    print("=" * 70)

    for step in result["trace"]:
        print(step)

    print("\n" + "=" * 70)
    print("FINAL RESPONSE")
    print("=" * 70)

    print(result["generated_answer"])