from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
from rapidfuzz import process

def get_closest_device_name(user_input, device_names):
    # Useing fuzzy matching to find the closest device name
    closest_match, score = process.extractOne(user_input, device_names)
    if score > 80:  # Seting a threshold for similarity
        return closest_match
    else:
        return None
def preprocessing(all_documents):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(all_documents)

    # Load the embedding model and embed the text chunks
    huggingface_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create the FAISS index directly using the embeddings and text chunks
    faiss_store = FAISS.from_documents(chunks, huggingface_embeddings)

    # Set up a retriever
    retriever = faiss_store.as_retriever(search_kwargs={"max_chunks": 5})
    return retriever

# Conversation history to store previous exchanges
conversation_history = []

def get_relevant_docs(query,retriever):
    docs = retriever.get_relevant_documents(query)
    relevant_chunks = [doc.page_content for doc in docs]
    return relevant_chunks

# Function to create RAG prompt with conversation memory
def make_rag_prompt(query, relevant_passage, history):
    relevant_passage = ' '.join(relevant_passage)
    
    # Include conversation history in the prompt
    history_text = " ".join([f"User: {item['question']}\nBot: {item['answer']}" for item in history])
    
    prompt = (
        f"You are a helpful and informative chatbot that answers questions using text from the reference passage below. "
        f"Respond in a complete sentence and make sure that your response is easy to understand for everyone. "
        f"Maintain a friendly and conversational tone. If the passage is irrelevant, feel free to ignore it.\n\n"
        f"Conversation History:\n{history_text}\n\n"
        f"QUESTION: '{query}'\n"
        f"PASSAGE: '{relevant_passage}'\n\n"
        f"ANSWER:"
    )
    return prompt

# Function to generate a response using Gemini
def generate_response(user_prompt):
    model = genai.GenerativeModel('gemini-pro')
    answer = model.generate_content(user_prompt)
    return answer.text