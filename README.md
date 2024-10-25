# Biomedical Chatbot Website
this Version of chatbot system to assist with medical device inquiries by using a Retrieval-Augmented Generation (RAG) approach. The chatbot categorizes medical devices by type, allowing users to search for information within a specific device category, rather than searching through all device PDFs. Key steps are:

## PDF Storage & Retrieval:

Device manuals are grouped by type (e.g., Imaging, ICU, etc.) in organized subfolders, each represented as a table in PostgreSQL.
The code dynamically creates tables for each folder and saves paths to device PDFs, enabling faster lookups within the correct category.
## Fuzzy Matching and Retrieval:

When a user asks a question, the chatbot identifies the closest matching device name (using fuzzy matching) within the chosen category.
Relevant device PDFs are then processed and split into smaller text chunks, embedded using HuggingFaceEmbeddings, and stored in a FAISS index for efficient search.
## Response Generation:

After retrieving relevant document chunks based on the query, a RAG-based prompt is constructed, incorporating past conversation context.
The chatbot uses the Gemini API to generate an answer that is easy to understand and conversationally friendly.
## Conversation Memory: Stores recent interactions, allowing the chatbot to maintain context for smoother and more relevant answers.

This approach ensures that questions about specific device types are answered efficiently, focusing only on relevant document segments, making it a scalable solution for extensive medical device libraries.

