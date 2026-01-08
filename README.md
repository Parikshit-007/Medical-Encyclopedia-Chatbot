# Medical Encyclopedia Chatbot

A ChatGPT-like interface for querying a medical encyclopedia using RAG (Retrieval-Augmented Generation).

## Features

- 🤖 Interactive chat interface similar to ChatGPT
- 📚 Medical encyclopedia knowledge base
- 🔍 Vector-based semantic search
- 💬 Real-time responses with source citations

## Project Structure

```
chatbot/
├── app.py                 # Flask API backend
├── connect_memory_with_llm.py  # Original chatbot script
├── create_memory_for_llm.py    # Vector store creation script
├── requirements.txt       # Python dependencies
├── frontend/             # React frontend
│   ├── src/
│   │   ├── App.js        # Main React component
│   │   ├── App.css       # Styling
│   │   └── index.js      # Entry point
│   └── package.json
└── vectorstore/          # FAISS vector database
```

## Setup Instructions

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pipenv install flask flask-cors
   # Or if using pip:
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   # Windows PowerShell
   $env:HF_TOKEN = "your-huggingface-token"
   
   # Or create a .env file (if using python-dotenv)
   ```

3. **Run the Flask API:**
   ```bash
   python app.py
   ```
   The API will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   The frontend will run on `http://localhost:3000`

## Usage

1. Start the backend API (port 5000)
2. Start the frontend React app (port 3000)
3. Open your browser to `http://localhost:3000`
4. Start asking medical questions!

## API Endpoints

### POST `/api/chat`
Send a question to the chatbot.

**Request:**
```json
{
  "question": "What is chemotherapy?"
}
```

**Response:**
```json
{
  "answer": "Chemotherapy is a treatment...",
  "source_page": "131",
  "success": true
}
```

### GET `/api/health`
Check if the API is running.

## Technologies Used

- **Backend:** Flask, LangChain, HuggingFace, FAISS
- **Frontend:** React, CSS3
- **Vector Store:** FAISS
- **LLM:** Mistral-7B-Instruct (via HuggingFace)

## Notes

- Make sure the vectorstore is created before running the API
- The chatbot only answers questions based on the medical encyclopedia content
- If the answer is not in the knowledge base, it will respond: "I don't have this information in my knowledge base."


