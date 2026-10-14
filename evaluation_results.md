# Self-RAG Agent — Evaluation Results
**Project:** University Course Advisory Agent  
**Course:** AI407L — Spring 2026  
**Date:** 2026-05-10  

---

## Test Case 1: Query where retrieval is NOT needed (greeting / general knowledge)
**Query:** `Hello! Can you help me with university information?`

**Expected Behavior:**  
Agent recognizes this as a greeting with no domain-specific query. Retrieval decision = skip_retrieval. Answers directly without touching the KB.

**Expected Path:** `skip_retrieval → generate_direct → END`

**Actual Path Taken:**
- [Node: decide_retrieval] Query received: 'Hello! Can you help me with university information?'
- [Node: decide_retrieval] Decision: SKIP_RETRIEVAL | Reason: The query is a greeting and introduction.
- [Node: generate_direct] Answering directly (no retrieval needed).
- [Node: generate_direct] Direct answer generated.

**Key Decisions:**
- Retrieval Decision: `skip_retrieval`
- Web Search Used: `False`
- Hallucination Verdict: `None`
- Retry Count: `0`
- Elapsed: `4.06s`

**Full Execution Trace:**
```
[Node: decide_retrieval] Query received: 'Hello! Can you help me with university information?'
[Node: decide_retrieval] Decision: SKIP_RETRIEVAL | Reason: The query is a greeting and introduction.
[Node: generate_direct] Answering directly (no retrieval needed).
[Node: generate_direct] Direct answer generated.
```

**Final Answer:**
> Hello. I'd be happy to help you with any university-related questions or concerns you might have. What specifically are you looking for? Are you considering applying to a university, looking for information on a particular course or program, or perhaps seeking advice on university life in general? Feel free to ask, and I'll do my best to assist you.

---

## Test Case 2: Query where retrieval IS needed and documents ARE relevant
**Query:** `What are the prerequisites and credit hours for the Data Structures course in the CS department?`

**Expected Behavior:**  
Agent identifies this as domain-specific. Retrieves CS catalog chunks. Grading marks them relevant. Generates grounded answer. Hallucination check passes.

**Expected Path:** `retrieve → grade_documents (relevant) → build_context → generate → hallucination_check (grounded) → END`

**Actual Path Taken:**
- [Node: decide_retrieval] Query received: 'What are the prerequisites and credit hours for the Data Structures course in the CS department?'
- [Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific course information.
- [Node: retrieve] Searching knowledge base for: 'What are the prerequisites and credit hours for the Data Structures course in the CS department?'
- [Node: retrieve] Retrieved 4 document chunks.
- [Node: grade_documents] Grading 4 retrieved documents...
- [Node: grade_documents] Relevant docs kept: 2 | Web search needed: False
- [Node: build_context] Context built from 2 relevant docs.
- [Node: generate] Generating answer (attempt 1)...
- [Node: generate] Answer generated (319 chars).
- [Node: hallucination_check] Checking answer (retry_count=1, max=3)...
- [Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately states that the context does not contain enough information to answer the question and correctly identifies the course title as 'CS-102: Data Structures & Algorithms'.

**Key Decisions:**
- Retrieval Decision: `retrieve`
- Web Search Used: `False`
- Hallucination Verdict: `grounded`
- Retry Count: `1`
- Elapsed: `66.84s`

**Full Execution Trace:**
```
[Node: decide_retrieval] Query received: 'What are the prerequisites and credit hours for the Data Structures course in the CS department?'
[Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific course information.
[Node: retrieve] Searching knowledge base for: 'What are the prerequisites and credit hours for the Data Structures course in the CS department?'
[Node: retrieve] Retrieved 4 document chunks.
  Doc[0] source=CS_Department_Catalog.pdf | first 80 chars: CS-202: Database Systems 
Credits: 3  |  Prerequisites: CS-102  |  Offered: Fall...
  Doc[1] source=CS_Department_Catalog.pdf | first 80 chars: XYZ National University 
Department of Computer Science — Course Catalog 2025–26...
  Doc[2] source=University_Academic_Policies.pdf | first 80 chars: 9. Academic Calendar 2025–26 
 
Event Fall 2025 Spring 2026 
Registration Opens ...
  Doc[3] source=University_Academic_Policies.pdf | first 80 chars: CGPA of 2.00 is required for graduation. Students falling below 1.50 CGPA for tw...
[Node: grade_documents] Grading 4 retrieved documents...
  Doc[0] → IRRELEVANT | The document chunk is about courses in the CS department, but none of them are Data Structures.
  Doc[1] → RELEVANT | The document chunk contains information about the CS-102 Data Structures & Algorithms course.
  Doc[2] → IRRELEVANT | The document chunk does not mention the Data Structures course or the CS department.
  Doc[3] → RELEVANT | The document chunk mentions a prerequisite policy for courses, which is relevant to the Data Structures course in the CS department.
[Node: grade_documents] Relevant docs kept: 2 | Web search needed: False
[Node: build_context] Context built from 2 relevant docs.
[Node: generate] Generating answer (attempt 1)...
[Node: generate] Answer generated (319 chars).
[Node: hallucination_check] Checking answer (retry_count=1, max=3)...
[Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately states that the context does not contain enough information to answer the question and correctly identifies the course title as 'CS-102: Data Structures & Algorithms'.
```

**Final Answer:**
> The context does not contain enough information to answer the question about the prerequisites and credit hours for the Data Structures course (CS-102) in the CS department, as the details for CS-102 are not fully provided. However, it is mentioned that the course exists, titled "CS-102: Data Structures & Algorithms".

---

## Test Case 3: Query where retrieval IS needed but documents are IRRELEVANT (web fallback)
**Query:** `What is the current acceptance rate and global university ranking of MIT?`

**Expected Behavior:**  
Agent retrieves from KB but MIT info isn't in the university catalog. All docs graded irrelevant. Web search fallback triggers. Answer generated from web results.

**Expected Path:** `retrieve → grade_documents (all irrelevant) → web_search → generate → hallucination_check → END`

**Actual Path Taken:**
- [Node: decide_retrieval] Query received: 'What is the current acceptance rate and global university ranking of MIT?'
- [Node: decide_retrieval] Decision: RETRIEVE | Reason: The query is about a specific university's global ranking, which is not directly related to the university's course catalog or policies.
- [Node: retrieve] Searching knowledge base for: 'What is the current acceptance rate and global university ranking of MIT?'
- [Node: retrieve] Retrieved 4 document chunks.
- [Node: grade_documents] Grading 4 retrieved documents...
- [Node: grade_documents] Relevant docs kept: 0 | Web search needed: True
- [Node: web_search] All KB docs irrelevant. Falling back to web search...
- [Node: web_search] Web search returned 3 results.
- [Node: generate] Generating answer (attempt 1)...
- [Node: generate] Answer generated (539 chars).
- [Node: hallucination_check] Checking answer (retry_count=1, max=3)...
- [Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately reflects the context, stating that the acceptance rate is 5% and that the global ranking is unclear. It does not invent any specific facts not present in the context.

**Key Decisions:**
- Retrieval Decision: `retrieve`
- Web Search Used: `True`
- Hallucination Verdict: `grounded`
- Retry Count: `1`
- Elapsed: `18.12s`

**Full Execution Trace:**
```
[Node: decide_retrieval] Query received: 'What is the current acceptance rate and global university ranking of MIT?'
[Node: decide_retrieval] Decision: RETRIEVE | Reason: The query is about a specific university's global ranking, which is not directly related to the university's course catalog or policies.
[Node: retrieve] Searching knowledge base for: 'What is the current acceptance rate and global university ranking of MIT?'
[Node: retrieve] Retrieved 4 document chunks.
  Doc[0] source=University_Academic_Policies.pdf | first 80 chars: XYZ National University 
Academic Policies & Regulations — 2025–26 
 
1. Grading...
  Doc[1] source=University_Academic_Policies.pdf | first 80 chars: Program Tuition Fee Lab Fee Total 
BS Computer Science PKR 185,000 PKR 25,000 PK...
  Doc[2] source=University_Academic_Policies.pdf | first 80 chars: the HoD. 
 
7. Course Withdrawal 
Students may withdraw from a course without ac...
  Doc[3] source=University_Academic_Policies.pdf | first 80 chars: 9. Academic Calendar 2025–26 
 
Event Fall 2025 Spring 2026 
Registration Opens ...
[Node: grade_documents] Grading 4 retrieved documents...
  Doc[0] → IRRELEVANT | The document chunk discusses grading system and GPA policies, not university rankings or acceptance rates.
  Doc[1] → IRRELEVANT | The document chunk contains information about tuition fees and courses at a different university, not MIT.
  Doc[2] → IRRELEVANT | The document chunk is about course withdrawal and degree requirements at an unspecified university, not MIT.
  Doc[3] → IRRELEVANT | The document chunk is about the academic calendar and transfer credit policy of a different university, not MIT.
[Node: grade_documents] Relevant docs kept: 0 | Web search needed: True
[Node: web_search] All KB docs irrelevant. Falling back to web search...
[Node: web_search] Web search returned 3 results.
  Web result: MIT University [Ranking 2026 + Acceptance Rate + Tuition] - EduRank
  Web result: Massachusetts Institute of Technology | US News Best Colleges
  Web result: Massachusetts Institute of Technology | World University Rankings
[Node: generate] Generating answer (attempt 1)...
[Node: generate] Answer generated (539 chars).
[Node: hallucination_check] Checking answer (retry_count=1, max=3)...
[Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately reflects the context, stating that the acceptance rate is 5% and that the global ranking is unclear. It does not invent any specific facts not present in the context.
```

**Final Answer:**
> According to the provided context, the current acceptance rate of MIT is 5%. However, the global university ranking of MIT is not consistently reported across the sources. One source mentions an MIT University ranked 11380th in the World, but this seems to refer to a different institution (possibly in North Macedonia). The more reputable sources (US News and Times Higher Education) do not provide a clear global ranking. Therefore, I can only confirm the acceptance rate, but the global ranking is unclear based on the provided context.

---

## Test Case 4: Hallucination check fails and agent regenerates
**Query:** `What is the exact tuition fee per credit hour and the GPA threshold for academic probation?`

**Expected Behavior:**  
If the first generation invents specific fee amounts not in the policy doc, the hallucination checker catches it and triggers a retry. The regenerated answer sticks to what the documents actually say.

**Expected Path:** `retrieve → grade_documents → build_context → generate → hallucination_check (hallucinated) → generate (retry) → hallucination_check (grounded) → END`

**Actual Path Taken:**
- [Node: decide_retrieval] Query received: 'What is the exact tuition fee per credit hour and the GPA threshold for academic probation?'
- [Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific university data (tuition fee and GPA threshold).
- [Node: retrieve] Searching knowledge base for: 'What is the exact tuition fee per credit hour and the GPA threshold for academic probation?'
- [Node: retrieve] Retrieved 4 document chunks.
- [Node: grade_documents] Grading 4 retrieved documents...
- [Node: grade_documents] Relevant docs kept: 2 | Web search needed: False
- [Node: build_context] Context built from 2 relevant docs.
- [Node: generate] Generating answer (attempt 1)...
- [Node: generate] Answer generated (443 chars).
- [Node: hallucination_check] Checking answer (retry_count=1, max=3)...
- [Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately reflects the information present in the context, stating that the tuition fee per credit hour is not mentioned and the GPA threshold for academic probation is a CGPA of 1.50 for two consecutive semesters, without inventing any specific facts not present in the context.

**Key Decisions:**
- Retrieval Decision: `retrieve`
- Web Search Used: `False`
- Hallucination Verdict: `grounded`
- Retry Count: `1`
- Elapsed: `20.23s`

**Full Execution Trace:**
```
[Node: decide_retrieval] Query received: 'What is the exact tuition fee per credit hour and the GPA threshold for academic probation?'
[Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific university data (tuition fee and GPA threshold).
[Node: retrieve] Searching knowledge base for: 'What is the exact tuition fee per credit hour and the GPA threshold for academic probation?'
[Node: retrieve] Retrieved 4 document chunks.
  Doc[0] source=University_Academic_Policies.pdf | first 80 chars: CGPA of 2.00 is required for graduation. Students falling below 1.50 CGPA for tw...
  Doc[1] source=University_Academic_Policies.pdf | first 80 chars: 9. Academic Calendar 2025–26 
 
Event Fall 2025 Spring 2026 
Registration Opens ...
  Doc[2] source=University_Academic_Policies.pdf | first 80 chars: XYZ National University 
Academic Policies & Regulations — 2025–26 
 
1. Grading...
  Doc[3] source=University_Academic_Policies.pdf | first 80 chars: Program Tuition Fee Lab Fee Total 
BS Computer Science PKR 185,000 PKR 25,000 PK...
[Node: grade_documents] Grading 4 retrieved documents...
  Doc[0] → RELEVANT | The document chunk mentions GPA threshold for academic probation and a CGPA requirement for graduation.
  Doc[1] → IRRELEVANT | The document chunk does not mention tuition fees or GPA thresholds for academic probation.
  Doc[2] → RELEVANT | The document chunk contains information about the university's grading system and GPA requirements.
  Doc[3] → IRRELEVANT | The document chunk does not mention tuition fee per credit hour or GPA threshold for academic probation.
[Node: grade_documents] Relevant docs kept: 2 | Web search needed: False
[Node: build_context] Context built from 2 relevant docs.
[Node: generate] Generating answer (attempt 1)...
[Node: generate] Answer generated (443 chars).
[Node: hallucination_check] Checking answer (retry_count=1, max=3)...
[Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately reflects the information present in the context, stating that the tuition fee per credit hour is not mentioned and the GPA threshold for academic probation is a CGPA of 1.50 for two consecutive semesters, without inventing any specific facts not present in the context.
```

**Final Answer:**
> The context does not contain information about the tuition fee per credit hour. However, it does mention a late registration fee of PKR 5,000.
> 
> Regarding the GPA threshold for academic probation, according to the context, students will be placed on academic probation if they fall below a CGPA of 1.50 for two consecutive semesters. There is no specific GPA (semester-based) threshold mentioned for academic probation, only the CGPA threshold.

---

## Test Case 5: Creative test — faculty lookup combining multiple document types
**Query:** `Which faculty members specialize in Artificial Intelligence and what courses do they teach?`

**Expected Behavior:**  
Agent retrieves from both the Faculty Directory and CS Department Catalog. Relevant faculty and their courses are assembled and answered correctly, with no fabricated names or course codes.

**Expected Path:** `retrieve → grade_documents → build_context → generate → hallucination_check → END`

**Actual Path Taken:**
- [Node: decide_retrieval] Query received: 'Which faculty members specialize in Artificial Intelligence and what courses do they teach?'
- [Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific faculty members and courses they teach, which requires looking up data from the knowledge base.
- [Node: retrieve] Searching knowledge base for: 'Which faculty members specialize in Artificial Intelligence and what courses do they teach?'
- [Node: retrieve] Retrieved 4 document chunks.
- [Node: grade_documents] Grading 4 retrieved documents...
- [Node: grade_documents] Relevant docs kept: 4 | Web search needed: False
- [Node: build_context] Context built from 4 relevant docs.
- [Node: generate] Generating answer (attempt 1)...
- [Node: generate] Answer generated (301 chars).
- [Node: hallucination_check] Checking answer (retry_count=1, max=3)...
- [Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately summarizes the context, stating that Dr. ilal ariq specializes in AI and Machine Learning, and teaching the specified courses. The answer does not invent any specific facts not present in the context.

**Key Decisions:**
- Retrieval Decision: `retrieve`
- Web Search Used: `False`
- Hallucination Verdict: `grounded`
- Retry Count: `1`
- Elapsed: `13.36s`

**Full Execution Trace:**
```
[Node: decide_retrieval] Query received: 'Which faculty members specialize in Artificial Intelligence and what courses do they teach?'
[Node: decide_retrieval] Decision: RETRIEVE | Reason: The query asks for specific faculty members and courses they teach, which requires looking up data from the knowledge base.
[Node: retrieve] Searching knowledge base for: 'Which faculty members specialize in Artificial Intelligence and what courses do they teach?'
[Node: retrieve] Retrieved 4 document chunks.
  Doc[0] source=CS_Department_Catalog.pdf | first 80 chars: strategies, and version control with Git. 
 
CS-350: Operating Systems 
Credits:...
  Doc[1] source=CS_Department_Catalog.pdf | first 80 chars: Search algorithms, knowledge representation, constraint satisfaction, probabilis...
  Doc[2] source=CS_Department_Catalog.pdf | first 80 chars: XYZ National University 
Department of Computer Science — Course Catalog 2025–26...
  Doc[3] source=Faculty_Directory.pdf | first 80 chars: XYZ National University 
Faculty Directory — 2025–26 
 
 
Name Department Design...
[Node: grade_documents] Grading 4 retrieved documents...
  Doc[0] → RELEVANT | The document chunk lists faculty members and courses related to Artificial Intelligence and Computer Science.
  Doc[1] → RELEVANT | The document chunk contains information about faculty members and courses related to Artificial Intelligence and Machine Learning.
  Doc[2] → RELEVANT | The document chunk is about the Department of Computer Science, which is relevant to the user's question about faculty members specializing in Artificial Intelligence.
  Doc[3] → RELEVANT | The document chunk lists faculty members from the Computer Science department, which specializes in Artificial Intelligence.
[Node: grade_documents] Relevant docs kept: 4 | Web search needed: False
[Node: build_context] Context built from 4 relevant docs.
[Node: generate] Generating answer (attempt 1)...
[Node: generate] Answer generated (301 chars).
[Node: hallucination_check] Checking answer (retry_count=1, max=3)...
[Node: hallucination_check] Verdict: GROUNDED | The generated answer accurately summarizes the context, stating that Dr. ilal ariq specializes in AI and Machine Learning, and teaching the specified courses. The answer does not invent any specific facts not present in the context.
```

**Final Answer:**
> According to the provided context, Dr. ilal ariq specializes in Artificial Intelligence (AI) and Machine Learning. He teaches the following courses:
> 
> 1. CS-302: Machine Learning
> 2. CS-501: Advanced Machine Learning
> 
> Note that Dr. ilal ariq is an Associate Professor in the Computer Science department.

---
