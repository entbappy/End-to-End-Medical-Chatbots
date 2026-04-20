# API Documentation

## 📋 Table of Contents

- [Overview](#overview)
- [Base URL](#base-url)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Request/Response Examples](#requestresponse-examples)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Integration Examples](#integration-examples)

---

## Overview

The Medical Chatbot API provides a simple interface for retrieving medical information through natural language queries. The API is built with Flask and uses a RAG (Retrieval-Augmented Generation) architecture to ensure accurate, context-grounded responses.

### Key Features

- ✅ Simple REST API
- ✅ Real-time response generation
- ✅ Context-aware medical Q&A
- ✅ JSON request/response format
- ✅ Error handling and validation

---

## Base URL

**Development**:
```
http://localhost:8080
```

**Production** (deployed):
```
http://your-domain.com
```

---

## Authentication

Currently, the API does **not require authentication**. However, for production deployments, consider adding:

- API key validation
- OAuth 2.0
- Rate limiting per client

**Future Implementation**:
```python
@app.before_request
def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or api_key != os.environ.get('API_KEY'):
        return jsonify({'error': 'Unauthorized'}), 401
```

---

## Endpoints

### 1. GET `/`

Returns the chat interface HTML page.

#### Description
Serves the user-facing chat interface for interacting with the chatbot.

#### Request

```http
GET / HTTP/1.1
Host: localhost:8080
```

#### Response

**Status**: `200 OK`

**Content-Type**: `text/html`

**Body**: HTML content of `templates/chat.html`

#### Example

```bash
curl http://localhost:8080/
```

---

### 2. POST `/get`

Processes user queries and returns AI-generated medical responses.

#### Description

This is the main endpoint for querying the medical chatbot. It:
1. Receives user query
2. Retrieves relevant documents from Pinecone
3. Generates response using GPT-4o
4. Returns answer grounded in the knowledge base

#### Request

**Method**: `POST`

**URL**: `/get`

**Content-Type**: `application/x-www-form-urlencoded` or `application/json`

#### Request Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `msg` | string | Yes | User's medical query | "What are the symptoms of diabetes?" |

#### Request Examples

**Using Form Data** (HTML Form):
```html
<form method="POST" action="/get">
    <input type="text" name="msg" value="What is hypertension?">
    <button type="submit">Send</button>
</form>
```

**Using cURL (Form Data)**:
```bash
curl -X POST http://localhost:8080/get \
  -d "msg=What are the symptoms of diabetes?"
```

**Using cURL (JSON)**:
```bash
curl -X POST http://localhost:8080/get \
  -H "Content-Type: application/json" \
  -d '{"msg":"What is heart disease?"}'
```

**Using Python Requests**:
```python
import requests

url = "http://localhost:8080/get"
data = {"msg": "What causes high blood pressure?"}

response = requests.post(url, data=data)
print(response.text)
```

**Using JavaScript Fetch**:
```javascript
const query = "What are risk factors for stroke?";

fetch('/get', {
    method: 'POST',
    body: new FormData(document.querySelector('form'))
})
.then(response => response.text())
.then(answer => console.log(answer))
.catch(error => console.error('Error:', error));
```

#### Response

**Status**: `200 OK`

**Content-Type**: `text/plain` or `text/html`

**Body**: Medical response text (plain string)

#### Response Examples

**Example 1**: Symptom Query
```
Request:
  msg = "What are the symptoms of diabetes?"

Response:
  Diabetes symptoms include increased thirst, frequent urination, and 
  unexplained weight loss. Additional signs may include fatigue, blurred vision, 
  and slow wound healing. Some people may experience tingling in hands or feet.
```

**Example 2**: Treatment Query
```
Request:
  msg = "How is hypertension treated?"

Response:
  Hypertension is typically managed through lifestyle modifications including 
  diet changes, regular exercise, and stress reduction. Medications such as 
  ACE inhibitors, beta-blockers, and diuretics are commonly prescribed. 
  Regular monitoring of blood pressure is essential.
```

**Example 3**: Unknown Query
```
Request:
  msg = "What is the capital of France?"

Response:
  I don't know the answer to that question based on the available medical knowledge base.
```

---

## Request/Response Examples

### Complete Flow Example

#### Scenario: User asks about heart disease

**1. Frontend (HTML)**:
```html
<form id="chatForm">
    <input type="text" id="userMessage" placeholder="Ask your medical question...">
    <button type="submit">Send</button>
</form>
<div id="response"></div>

<script>
document.getElementById('chatForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const msg = document.getElementById('userMessage').value;
    
    const formData = new FormData();
    formData.append('msg', msg);
    
    const response = await fetch('/get', {
        method: 'POST',
        body: formData
    });
    
    const answer = await response.text();
    document.getElementById('response').textContent = answer;
});
</script>
```

**2. Flask Backend (app.py)**:
```python
@app.route("/get", methods=["GET", "POST"])
def chat():
    msg = request.form["msg"]  # "What are risk factors for heart disease?"
    
    # Pass to RAG chain
    response = rag_chain.invoke({"input": msg})
    
    return str(response["answer"])
```

**3. LangChain Pipeline**:
```
Query: "What are risk factors for heart disease?"
       ↓
Embed query to 384-dim vector
       ↓
Search Pinecone for similar documents (top 3)
       ↓
Retrieved Documents:
  - "Heart disease risk factors include high blood pressure, high cholesterol..."
  - "Lifestyle factors like smoking and lack of exercise increase risk..."
  - "Family history and age are significant risk factors..."
       ↓
Create Prompt with system instruction + context + query
       ↓
Call GPT-4o LLM
       ↓
Response: "Heart disease risk factors include high blood pressure, 
high cholesterol, smoking, obesity, and lack of physical activity. 
Family history and advancing age are also significant risk factors."
```

---

## Error Handling

### Possible Errors

#### 1. Missing Query Parameter

**Error Type**: Client Error

**Condition**: User doesn't provide `msg` parameter

**Response Status**: `400 Bad Request`

**Example**:
```bash
curl -X POST http://localhost:8080/get
# Error: 'msg' not provided
```

**Solution**: Always include `msg` parameter

#### 2. API Key Invalid

**Error Type**: Authentication Error

**Condition**: Invalid OpenAI or Pinecone API key

**Response Status**: `401 Unauthorized`

**Response Body**:
```json
{
    "error": "Invalid API credentials",
    "details": "Failed to authenticate with OpenAI/Pinecone"
}
```

**Solution**: Verify API keys in `.env` file

#### 3. Database Connection Error

**Error Type**: Server Error

**Condition**: Cannot connect to Pinecone

**Response Status**: `503 Service Unavailable`

**Response Body**:
```json
{
    "error": "Database connection failed",
    "details": "Unable to reach Pinecone index"
}
```

**Solution**: Check Pinecone service status and API key

#### 4. LLM Rate Limit

**Error Type**: Server Error

**Condition**: Too many requests to OpenAI in short time

**Response Status**: `429 Too Many Requests`

**Solution**: Implement request queuing or wait before retrying

#### 5. Server Error

**Error Type**: Server Error

**Condition**: Unexpected server-side error

**Response Status**: `500 Internal Server Error`

**Solution**: Check server logs for details

### Error Response Format (Future)

```json
{
    "success": false,
    "error": {
        "code": "API_ERROR_CODE",
        "message": "Human-readable error message",
        "details": "Technical details for debugging"
    },
    "timestamp": "2024-04-20T10:30:00Z"
}
```

---

## Rate Limiting

### Current Status

Currently **no rate limiting** is implemented. For production, consider:

### Recommended Rate Limits

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route("/get", methods=["POST"])
@limiter.limit("10 per minute")
def chat():
    # Implementation
    pass
```

### Rate Limit Headers (Future)

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1713610200
```

---

## Integration Examples

### Python Integration

#### Using Requests Library

```python
import requests
import json

class MedicalChatbotClient:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def ask(self, question):
        """Query the chatbot"""
        response = requests.post(
            f"{self.base_url}/get",
            data={"msg": question}
        )
        
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Error: {response.status_code}")

# Usage
client = MedicalChatbotClient()
answer = client.ask("What is diabetes?")
print(answer)
```

#### Using LangChain Directly

```python
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI

# Initialize components
embeddings = download_hugging_face_embeddings()
vector_store = PineconeVectorStore.from_existing_index(
    index_name="medical-chatbot",
    embedding=embeddings
)

retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}
)

# Custom query
query = "What causes diabetes?"
docs = retriever.get_relevant_documents(query)

print("Retrieved documents:")
for doc in docs:
    print(f"- {doc.page_content[:100]}...")
```

### JavaScript Integration

#### Vanilla JavaScript

```javascript
class MedicalChatbot {
    constructor(baseUrl = 'http://localhost:8080') {
        this.baseUrl = baseUrl;
    }
    
    async ask(question) {
        const formData = new FormData();
        formData.append('msg', question);
        
        try {
            const response = await fetch(`${this.baseUrl}/get`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.text();
        } catch (error) {
            console.error('Error:', error);
            return null;
        }
    }
}

// Usage
const chatbot = new MedicalChatbot();
chatbot.ask("What are symptoms of asthma?").then(answer => {
    console.log("Answer:", answer);
});
```

#### React Integration

```javascript
import React, { useState } from 'react';

function MedicalChatbot() {
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const formData = new FormData();
            formData.append('msg', question);
            
            const response = await fetch('/get', {
                method: 'POST',
                body: formData
            });
            
            const text = await response.text();
            setAnswer(text);
        } catch (error) {
            setAnswer('Error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <div>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="Ask a medical question..."
                />
                <button type="submit" disabled={loading}>
                    {loading ? 'Loading...' : 'Send'}
                </button>
            </form>
            
            {answer && <div className="answer">{answer}</div>}
        </div>
    );
}

export default MedicalChatbot;
```

### cURL Examples

**Basic Query**:
```bash
curl -X POST http://localhost:8080/get \
  -d "msg=What is heart disease?"
```

**With Headers**:
```bash
curl -X POST http://localhost:8080/get \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "msg=What are treatments for hypertension?" \
  -v
```

**Save Response to File**:
```bash
curl -X POST http://localhost:8080/get \
  -d "msg=Explain diabetes" \
  -o response.txt
```

**Multiple Queries**:
```bash
for query in "What is diabetes?" "How to treat asthma?" "Symptoms of fever?"; do
    echo "Query: $query"
    curl -s -X POST http://localhost:8080/get -d "msg=$query"
    echo -e "\n---\n"
done
```

---

## Best Practices

### 1. Query Structure

**Good Queries**:
- Clear and specific
- Medical terminology accurate
- Reasonable length (1-2 sentences)

**Examples**:
- ✅ "What are the symptoms of type 2 diabetes?"
- ✅ "How is hypertension diagnosed?"
- ✅ "What are side effects of aspirin?"

**Bad Queries**:
- ❌ "disease symptoms" (too vague)
- ❌ "medical stuff" (not specific)
- ❌ Very long questions (truncate if needed)

### 2. Error Handling

Always implement proper error handling:

```python
try:
    response = requests.post("/get", data={"msg": query})
    response.raise_for_status()
    answer = response.text
except requests.exceptions.ConnectionError:
    print("Cannot connect to chatbot server")
except requests.exceptions.Timeout:
    print("Request timed out")
except Exception as e:
    print(f"Error: {e}")
```

### 3. Caching

Cache frequently asked questions to improve performance:

```python
import functools
import time

@functools.lru_cache(maxsize=100)
def get_cached_answer(question):
    response = requests.post("/get", data={"msg": question})
    return response.text
```

### 4. Timeout Handling

Implement timeout for long-running requests:

```python
response = requests.post(
    "/get",
    data={"msg": query},
    timeout=30  # 30 second timeout
)
```

---

## Response Format Future Enhancement

Current response is plain text. Future versions should return structured JSON:

```json
{
    "success": true,
    "data": {
        "answer": "Diabetes is a chronic condition...",
        "confidence": 0.92,
        "sources": [
            {
                "document": "medical_guide.pdf",
                "page": 42,
                "excerpt": "..."
            }
        ],
        "processing_time_ms": 1234
    }
}
```

---

## Changelog

### Version 1.0 (Current)
- ✅ Basic `/get` endpoint
- ✅ HTML chat interface
- ✅ RAG-based question answering

### Version 1.1 (Planned)
- 🔄 JSON response format
- 🔄 Authentication/API keys
- 🔄 Rate limiting
- 🔄 Response confidence scores
- 🔄 Source document references

### Version 2.0 (Future)
- 🔄 Streaming responses
- 🔄 Multi-turn conversations
- 🔄 User feedback mechanism
- 🔄 Analytics dashboard
- 🔄 Custom knowledge bases
