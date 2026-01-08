from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize chatbot components (load once at startup)
HF_TOKEN = os.environ.get("HF_TOKEN")
huggingface_repo_id = "mistralai/Mistral-7B-Instruct-v0.2"
DB_FAISS_PATH = "vectorstore/db_faiss"

# Load LLM
def load_llm(repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=repo_id,
        task="conversational",
        huggingfacehub_api_token=HF_TOKEN,
        temperature=0.5,
        max_new_tokens=512
    )
    chat_llm = ChatHuggingFace(llm=llm)
    return chat_llm

# Load embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embeddings, allow_dangerous_deserialization=True)

# Custom prompt template
custom_prompt_template = """
You are a medical encyclopedia assistant. Answer the question ONLY if the provided context directly contains the answer. 

IMPORTANT RULES:
- If the context does NOT directly answer the question, you MUST respond with: "I don't have this information in my knowledge base."
- Do NOT make up answers or use information not in the context.
- Do NOT provide general knowledge that is not in the context.
- Only use information explicitly stated in the context below.

Question: {question}

Context: {context}

Answer (ONLY if context directly answers the question, otherwise say "I don't have this information in my knowledge base."):
"""

def custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(template=custom_prompt_template, input_variables=["question", "context"])
    return prompt

# Initialize QA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_llm(huggingface_repo_id), 
    chain_type="stuff", 
    retriever=db.as_retriever(search_kwargs={"k": 3}), 
    return_source_documents=True, 
    chain_type_kwargs={"prompt": custom_prompt(custom_prompt_template)}
)

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': 'Question is required'}), 400
        
        # Get response from chatbot
        result = qa_chain.invoke({"query": question})
        
        # Extract source page
        source_page = result['source_documents'][0].metadata.get('page_label', 'N/A') if result['source_documents'] else 'N/A'
        
        return jsonify({
            'answer': result['result'],
            'source_page': source_page,
            'success': True
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)

