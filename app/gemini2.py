from app.models import get_pdf_paths, get_subfolder
from rapidfuzz import process
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import HuggingFaceHub
from langchain_community.document_loaders import PyPDFLoader
import google.generativeai as genai
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from app.functions import *


GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')



# Main function to handle the entire workflow
def ask_question(query, category,device):
    # Fetch the device names based on the category
    device_names = get_subfolder(category)

    # Get the closest device name based on user input
    device = get_closest_device_name(device, device_names)
    pdf_paths = get_pdf_paths(category, device)

    # Load and process the PDF documents
    all_documents = []
    for path in pdf_paths:
        loader = PyPDFLoader(path)
        documents = loader.load()
        all_documents.extend(documents)

    retriever = preprocessing(all_documents)

    # Retrieve relevant chunks based on the query
    relevant_text = get_relevant_docs(query, retriever)

    # Generate the prompt for RAG
    prompt = make_rag_prompt(query, relevant_passage=relevant_text, history=conversation_history)

    # Generate the response
    answer = generate_response(prompt)

    # Store the current query and answer in the conversation history
    conversation_history.append({'question': query, 'answer': answer})

    # Limit the conversation history to the last 5 exchanges
    if len(conversation_history) > 5:
        conversation_history.pop(0)

    return answer


