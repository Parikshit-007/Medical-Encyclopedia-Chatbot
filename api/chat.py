from http.server import BaseHTTPRequestHandler
import json
import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Global variables for caching (loaded once per serverless instance)
qa_chain = None

def initialize_chatbot():
    global qa_chain
    
    if qa_chain is not None:
        return qa_chain
    
    try:
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
        
        return qa_chain
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        raise

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Initialize chatbot if not already done
            chain = initialize_chatbot()
            
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            question = data.get('question', '')
            
            if not question:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Question is required',
                    'success': False
                }).encode())
                return
            
            # Get response from chatbot
            result = chain.invoke({"query": question})
            
            # Extract source page
            source_page = result['source_documents'][0].metadata.get('page_label', 'N/A') if result['source_documents'] else 'N/A'
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'answer': result['result'],
                'source_page': source_page,
                'success': True
            }).encode())
        
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'error': str(e),
                'success': False
            }).encode())

