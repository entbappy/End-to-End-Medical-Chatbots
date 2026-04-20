# System Architecture

## 📋 Table of Contents

- [High-Level Overview](#high-level-overview)
- [Component Breakdown](#component-breakdown)
- [Data Flow](#data-flow)
- [RAG Pipeline](#rag-pipeline)
- [Technology Choices](#technology-choices)
- [Scalability Considerations](#scalability-considerations)

---

## High-Level Overview

The Medical Chatbot is built on the **Retrieval-Augmented Generation (RAG)** paradigm, which combines:

1. **Information Retrieval**: Vector similarity search in a knowledge base
2. **Language Generation**: LLM-based response generation conditioned on retrieved context
3. **Web Interface**: Flask-based user-facing application

This architecture ensures responses are **grounded in verified medical knowledge**, reducing hallucinations and improving reliability.

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                     USER INTERACTION LAYER                          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              Web Browser (HTML/CSS/JavaScript)               │  │
│  │               Chat Interface at :8080                        │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER (Flask)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  app.py - Flask Application Server                          │  │
│  │  • Route: GET /     → Serve chat.html                       │  │
│  │  • Route: POST /get → Process user query                    │  │
│  │  • Environment Config Loading                               │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER (LangChain)                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  RAG Chain Components:                                       │  │
│  │  1. Retriever (Pinecone Vector Store)                       │  │
│  │  2. Document Formatter                                       │  │
│  │  3. Prompt Template Manager                                  │  │
│  │  4. LLM (ChatOpenAI)                                         │  │
│  └──────────────────────┬───────────────────────────────────────┘  │
└────────────────────────┼──────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  Pinecone    │  │  OpenAI      │  │ HuggingFace  │
│  Vector DB   │  │  GPT-4o      │  │ Embeddings   │
│  (Retrieve)  │  │  (Generate)  │  │ (Embed)      │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Component Breakdown

### 1. Frontend Layer

**Files**: `templates/chat.html`, `static/style.css`

**Responsibilities**:
- Provides user-friendly chat interface
- Handles user input and message display
- Makes AJAX requests to backend `/get` endpoint
- Real-time message updates

**Key Features**:
- Responsive design for mobile/desktop
- Message history display
- Loading indicators
- Error handling and user feedback

---

### 2. Application Layer (Flask)

**File**: `app.py`

**Responsibilities**:
- HTTP request routing
- Environment variable loading
- Component initialization (embeddings, vector store, LLM)
- Request/response handling

**Key Routes**:

```python
@app.route("/")
def index():
    # Serves the chat interface
    return render_template('chat.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    # Processes user queries
    msg = request.form["msg"]
    response = rag_chain.invoke({"input": msg})
    return str(response["answer"])
```

**Initialization**:

```python
# Load environment variables
load_dotenv()

# Download embeddings model
embeddings = download_hugging_face_embeddings()

# Connect to Pinecone index
docsearch = PineconeVectorStore.from_existing_index(
    index_name="medical-chatbot",
    embedding=embeddings
)

# Initialize LLM
chatModel = ChatOpenAI(model="gpt-4o")

# Create RAG chain
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
```

---

### 3. Orchestration Layer (LangChain)

**Responsibilities**:
- Manages retrieval pipeline
- Handles prompt templates
- Chains together LLM calls
- Document formatting

**Components**:

#### 3.1 Retriever

```python
retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Return top 3 similar documents
)
```

- Uses Pinecone vector store
- Performs semantic similarity search
- Returns top-k most relevant documents

#### 3.2 Prompt Template

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),  # Medical assistant persona
    ("human", "{input}"),       # User query
])
```

System prompt (from `src/prompt.py`):
```
"You are a Medical assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer 
the question. If you don't know the answer, say that you 
don't know. Use three sentences maximum and keep the 
answer concise."
```

#### 3.3 Document Chain

```python
question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
```

- Formats retrieved documents into the prompt
- "Stuff" method: Directly includes documents in prompt (good for small document counts)

#### 3.4 Retrieval Chain

```python
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
```

- Orchestrates the complete RAG pipeline
- Retrieves relevant documents
- Generates response based on context

---

### 4. Data Layer

#### 4.1 Vector Database (Pinecone)

**Purpose**: Semantic search and similarity matching

**Configuration**:
- Index name: `medical-chatbot`
- Metric: Cosine similarity
- Dimension: 384 (from HuggingFace embeddings)

**Operations**:
- **Upsert** (store_index.py): Add embeddings to index
- **Query** (app.py): Search for similar documents

#### 4.2 External APIs

**OpenAI GPT-4o**:
- Endpoint: OpenAI API
- Model: gpt-4o
- Purpose: Generate response text
- Requires: OPENAI_API_KEY

**HuggingFace Embeddings**:
- Model: sentence-transformers/all-MiniLM-L6-v2
- Purpose: Convert text to 384-dimensional vectors
- Access: Automatically downloaded on first use

---

### 5. Data Preparation Pipeline

**File**: `store_index.py`

**Process Flow**:

```
┌─────────────────────────────────────┐
│  Medical PDF Documents (data/)      │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Load PDFs (PyPDFLoader)            │
│  • Extract text from all PDFs       │
│  • Preserve metadata (source file)  │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Split Text (RecursiveCharacterSplitter)
│  • Chunk size: 500 characters       │
│  • Overlap: 20 characters           │
│  • Preserve chunk boundaries        │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Generate Embeddings (HuggingFace)  │
│  • Model: all-MiniLM-L6-v2          │
│  • Dimension: 384                   │
│  • Vectorize each chunk             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  Upsert to Pinecone                 │
│  • Store vectors + metadata         │
│  • Index for fast retrieval         │
└─────────────────────────────────────┘
```

**Key Functions**:

- `load_pdf_file(data)`: Load PDFs from directory
- `text_split(extracted_data)`: Split into chunks
- `download_hugging_face_embeddings()`: Get embedding model
- `store_index.py`: Orchestrate entire pipeline

---

## RAG Pipeline

### Query Processing Flow

```
User Query: "What are symptoms of diabetes?"
            │
            ▼
    ┌───────────────────┐
    │  User Input (Web) │
    └────────┬──────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ 1. Embed Query                    │
    │    • Convert to 384-dim vector    │
    │    • Using HuggingFace model      │
    └────────┬────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ 2. Retrieve Similar Documents     │
    │    • Pinecone similarity search   │
    │    • Top-k=3 results              │
    │                                    │
    │ Results:                           │
    │ - Doc1: "Diabetes types and..."   │
    │ - Doc2: "Symptoms include..."     │
    │ - Doc3: "Risk factors..."         │
    └────────┬────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ 3. Format Context                 │
    │    • Combine retrieved docs       │
    │    • Add source metadata          │
    └────────┬────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ 4. Create Prompt                  │
    │                                    │
    │ System: "You are a medical..."    │
    │ Context: [Retrieved docs]         │
    │ Query: "What are symptoms..."     │
    └────────┬────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ 5. Call LLM (GPT-4o)              │
    │    • Process prompt               │
    │    • Generate response            │
    │    • Max 3 sentences              │
    └────────┬────────────────────────┘
             │
             ▼
    ┌───────────────────────────────────┐
    │ Response: "Diabetes symptoms...   │
    │ include increased thirst..."      │
    └───────────────────────────────────┘
```

---

## Technology Choices

### Why RAG?

1. **Accuracy**: Responses grounded in verified knowledge base
2. **Explainability**: Retrieved documents show source of information
3. **Cost Efficiency**: Smaller context than fine-tuning
4. **Flexibility**: Easy to update knowledge base without retraining

### Why Pinecone?

- ✅ Managed vector database (no infrastructure overhead)
- ✅ Serverless (auto-scaling)
- ✅ Fast similarity search
- ✅ Built-in metadata filtering
- ✅ Excellent documentation

### Why GPT-4o?

- ✅ State-of-the-art reasoning and generation
- ✅ Handles medical terminology well
- ✅ Multimodal capabilities (images, text)
- ✅ Reliable API
- ✅ Good for context length

### Why HuggingFace Embeddings?

- ✅ All-MiniLM-L6-v2: Lightweight, fast, good quality
- ✅ 384-dimensional: Good balance of speed/quality
- ✅ Open-source and free
- ✅ Works offline once downloaded

---

## Scalability Considerations

### Current Limitations

- **Deployment**: Single EC2 instance (not load-balanced)
- **Concurrent Users**: Limited by single Flask process
- **Knowledge Base Size**: Pinecone handles millions of vectors

### Future Improvements

#### Horizontal Scaling

```
┌──────────────────────────────┐
│  Load Balancer (ALB/NLB)     │
└───────────┬──────────────────┘
            │
    ┌───────┼───────┬────────┐
    │       │       │        │
    ▼       ▼       ▼        ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│ EC2  │ │ EC2  │ │ EC2  │ │ EC2  │
│ Pod1 │ │ Pod2 │ │ Pod3 │ │ Pod4 │
└──────┘ └──────┘ └──────┘ └──────┘
    │       │       │        │
    └───────┼───────┼────────┘
            │
            ▼
    ┌──────────────────┐
    │ Pinecone (Shared)│
    └──────────────────┘
```

#### Caching Layer

- Add Redis cache for frequently asked questions
- Cache query embeddings
- Cache API responses

#### Rate Limiting

- Implement per-user rate limits
- Queue system for high-traffic periods
- Priority queue for medical emergencies

#### Monitoring

- Application Performance Monitoring (APM)
- Error tracking and logging
- Latency monitoring per component

---

## Security Considerations

### API Keys Management

```python
# ✅ Good: Environment variables
from dotenv import load_dotenv
load_dotenv()
PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

# ❌ Bad: Hardcoded secrets
PINECONE_API_KEY = "pk_xxxxx"
```

### Input Validation

- Validate user input length
- Sanitize HTML/JavaScript injection attempts
- Rate limiting on endpoints

### CORS and Security Headers

- Restrict CORS origins
- Add security headers (CSP, X-Frame-Options, etc.)
- HTTPS only in production

### Data Privacy

- No personal health information (PHI) storage
- Ensure HIPAA compliance if needed
- Log minimal user data

---

## Monitoring and Observability

### Key Metrics to Track

1. **Query Latency**: Time from user input to response
2. **Retrieval Quality**: Relevance of retrieved documents
3. **Response Quality**: Factuality and usefulness
4. **Error Rate**: Failed queries percentage
5. **API Usage**: Token consumption for OpenAI and Pinecone

### Logging Strategy

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Log important events
logger.info(f"User query: {user_query}")
logger.error(f"API error: {error}")
```

---

## Conclusion

This architecture provides a robust, scalable foundation for a medical chatbot. The use of RAG ensures reliable, verifiable responses while remaining flexible for future enhancements and scaling.
