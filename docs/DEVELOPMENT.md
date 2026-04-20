# Development Guide

## 📋 Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Style Guidelines](#code-style-guidelines)
- [Key Components](#key-components)
- [Running Tests](#running-tests)
- [Debugging](#debugging)
- [Contributing Guidelines](#contributing-guidelines)
- [Common Development Tasks](#common-development-tasks)

---

## Development Setup

### Prerequisites

- Python 3.10+
- Git
- API keys (OpenAI, Pinecone)
- Virtual environment (conda, venv, or uv)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/entbappy/End-to-End-Medical-Chatbot.git
cd End-to-End-Medical-Chatbot

# Create virtual environment
conda create -n medibot-dev python=3.10 -y
conda activate medibot-dev

# Install dependencies with dev extras
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 ipython

# Copy example env file
cp .env.example .env
# Edit .env with your API keys
```

### IDE Setup

#### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "[python]": {
        "editor.formatOnSave": true,
        "editor.defaultFormatter": "ms-python.python"
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true,
        "**/.egg-info": true
    }
}
```

#### PyCharm

1. Set interpreter: Settings → Project → Python Interpreter
2. Enable code inspections: Settings → Editor → Inspections
3. Configure code style: Settings → Editor → Code Style → Python

---

## Project Structure

### Core Application Files

```
src/
├── __init__.py              # Package initialization
├── helper.py                # Utility functions
│   ├── load_pdf_file()      # Load PDFs from directory
│   ├── text_split()         # Split text into chunks
│   └── download_hugging_face_embeddings()
├── prompt.py                # System prompts
│   └── system_prompt        # Chatbot system instruction

app.py                        # Main Flask application
store_index.py               # Data indexing script
```

### Frontend Files

```
templates/
└── chat.html                # Chat interface template

static/
└── style.css                # Chat UI styling
```

### Configuration Files

```
requirements.txt             # Python dependencies
setup.py                     # Package setup
Dockerfile                   # Docker configuration
.env.example                 # Example environment variables
.gitignore                   # Git ignore rules
```

---

## Code Style Guidelines

### Python Style (PEP 8)

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications.

#### Formatting with Black

```bash
# Format single file
black src/helper.py

# Format entire project
black .

# Check formatting without modifying
black --check .
```

#### Linting with Flake8

```bash
# Check for style issues
flake8 src/ app.py

# Ignore specific rules
flake8 src/ --ignore=E501,W503
```

### Naming Conventions

```python
# ✅ Good
class DocumentProcessor:
    def load_pdf_file(self, file_path: str) -> list:
        pass

def calculate_similarity(vec1, vec2) -> float:
    pass

MAX_CHUNK_SIZE = 500
DEFAULT_MODEL = "gpt-4o"

# ❌ Bad
class doc_processor:  # Use PascalCase for classes
    def LoadPDFFile(self):  # Use snake_case for functions
        pass

max_chunk_size = 500  # Use UPPER_SNAKE_CASE for constants
```

### Type Hints

```python
# ✅ Good - Always use type hints
from typing import List, Dict, Optional

def process_documents(
    files: List[str],
    chunk_size: int = 500,
    metadata: Optional[Dict] = None
) -> List[str]:
    """Process documents and return text chunks."""
    pass

# ❌ Bad - Missing type hints
def process_documents(files, chunk_size=500, metadata=None):
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def load_pdf_file(data_directory: str) -> List[Document]:
    """Load PDF documents from a directory.
    
    This function loads all PDF files from the specified directory
    using PyPDFLoader and DirectoryLoader.
    
    Args:
        data_directory: Path to directory containing PDF files.
        
    Returns:
        List of Document objects extracted from PDFs.
        
    Raises:
        FileNotFoundError: If directory doesn't exist.
        ValueError: If no PDF files found in directory.
        
    Example:
        >>> docs = load_pdf_file('./data')
        >>> len(docs)
        5
    """
    pass
```

### Comments

```python
# ✅ Good - Explains why, not what
# Use cosine similarity for medical text matching as it's
# more robust to document length variations
embedding_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

# ❌ Bad - Redundant with code
embedding_model = HuggingFaceEmbeddings(...)  # Create embedding model
```

---

## Key Components

### 1. PDF Processing (`src/helper.py`)

**Function**: Load and process medical PDFs

```python
def load_pdf_file(data: str) -> List[Document]:
    """
    Load PDF files from directory.
    
    Uses PyPDFLoader for individual files and DirectoryLoader
    for batch processing with glob patterns.
    """
    loader = DirectoryLoader(
        data,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    return loader.load()
```

**Considerations**:
- PDFs should be text-based, not scanned images
- Large PDFs (>100MB) may cause memory issues
- PDF quality affects extraction accuracy

### 2. Text Splitting (`src/helper.py`)

**Function**: Split documents into chunks for embeddings

```python
def text_split(extracted_data: List[Document]) -> List[Document]:
    """
    Split text into chunks for embedding.
    
    Uses RecursiveCharacterTextSplitter with:
    - chunk_size: 500 characters
    - chunk_overlap: 20 characters
    
    Overlap helps preserve context at chunk boundaries.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=20
    )
    return text_splitter.split_documents(extracted_data)
```

**Parameters to Tune**:
- `chunk_size`: Smaller = more granular retrieval, more requests
- `chunk_overlap`: Prevents losing context at boundaries

### 3. Embeddings (`src/helper.py`)

**Function**: Convert text to vectors

```python
def download_hugging_face_embeddings():
    """
    Download and initialize HuggingFace embeddings.
    
    Model: sentence-transformers/all-MiniLM-L6-v2
    - 384-dimensional vectors
    - Lightweight and fast
    - Good for semantic similarity
    
    Downloaded on first use, cached locally (~40MB).
    """
    embeddings = HuggingFaceEmbeddings(
        model_name='sentence-transformers/all-MiniLM-L6-v2'
    )
    return embeddings
```

**Model Options**:
- Current: `all-MiniLM-L6-v2` (384 dims, fast)
- Alternative: `all-mpnet-base-v2` (768 dims, better quality)

### 4. Flask Application (`app.py`)

**Routes**:
- `GET /`: Serve chat interface
- `POST /get`: Process queries

**Key Flow**:

```python
@app.route("/get", methods=["POST"])
def chat():
    # 1. Get user message
    msg = request.form["msg"]
    
    # 2. Pass to RAG chain
    response = rag_chain.invoke({"input": msg})
    
    # 3. Return answer
    return str(response["answer"])
```

**Improvement Ideas**:
- Add logging for debugging
- Implement error handling
- Add request validation
- Add response metadata (sources, confidence)

### 5. RAG Chain (`app.py`)

**Components**:

```python
# 1. Retriever - Find relevant documents
retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 3}  # Top 3 most similar
)

# 2. Prompt - Provide context and instructions
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 3. LLM - Generate response
chatModel = ChatOpenAI(model="gpt-4o")

# 4. Chain - Orchestrate pipeline
question_answer_chain = create_stuff_documents_chain(
    chatModel, prompt
)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)
```

**Customization Options**:
- Change retrieval method: `search_type="mmr"` (Maximal Marginal Relevance)
- Change top-k: `search_kwargs={"k": 5}`
- Change LLM model: `ChatOpenAI(model="gpt-4-turbo")`

---

## Running Tests

### Test Structure

```
tests/
├── __init__.py
├── test_helper.py           # Test helper functions
├── test_prompt.py           # Test prompt generation
└── test_integration.py      # Test full pipeline
```

### Writing Tests

```python
import pytest
from src.helper import load_pdf_file, text_split

class TestPDFLoading:
    """Tests for PDF loading functionality."""
    
    def test_load_pdf_valid_directory(self):
        """Test loading PDFs from valid directory."""
        docs = load_pdf_file("./data")
        assert len(docs) > 0
    
    def test_load_pdf_empty_directory(self):
        """Test loading from directory with no PDFs."""
        with pytest.raises(ValueError):
            load_pdf_file("./empty")

class TestTextSplitting:
    """Tests for text splitting functionality."""
    
    def test_split_creates_chunks(self):
        """Test that text is split into chunks."""
        docs = load_pdf_file("./data")
        chunks = text_split(docs)
        assert len(chunks) > len(docs)
    
    def test_split_preserves_content(self):
        """Test that splitting doesn't lose content."""
        docs = load_pdf_file("./data")
        chunks = text_split(docs)
        
        original_length = sum(len(d.page_content) for d in docs)
        chunk_length = sum(len(c.page_content) for c in chunks)
        
        # Account for overlap
        assert chunk_length >= original_length
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_helper.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_helper.py::TestPDFLoading::test_load_pdf_valid_directory
```

---

## Debugging

### Enabling Debug Mode

```python
# In app.py
app.run(debug=True)  # Enable auto-reload and debugger
```

### Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.debug(f"Received query: {msg}")
logger.info(f"Retrieved {len(docs)} documents")
logger.warning(f"Low confidence response: {confidence}")
logger.error(f"API error: {error}")
```

### Interactive Debugging

#### Using pdb

```python
import pdb

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form["msg"]
    
    pdb.set_trace()  # Debugger will pause here
    response = rag_chain.invoke({"input": msg})
    
    return str(response["answer"])
```

#### Using ipdb (Better)

```bash
pip install ipdb

# In code
import ipdb; ipdb.set_trace()
```

#### Using Python Debugger

```bash
python -m pdb app.py
```

### Useful Debugging Commands

```python
# In pdb/ipdb prompt
(Pdb) l              # List current code
(Pdb) n              # Next line
(Pdb) s              # Step into function
(Pdb) c              # Continue execution
(Pdb) p variable     # Print variable
(Pdb) w              # Show stack trace
(Pdb) h              # Help
```

---

## Contributing Guidelines

### Making Changes

1. **Create feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes**:
   ```bash
   # Edit files
   git add .
   git commit -m "Add feature: description"
   ```

3. **Run tests and linting**:
   ```bash
   pytest
   black .
   flake8 .
   ```

4. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `test`: Test additions
- `chore`: Build/dependency updates

**Examples**:
```
feat: Add caching for frequently asked questions

fix: Handle empty PDF files gracefully

docs: Add architecture diagram to README

chore: Update dependencies to latest versions
```

### Pull Request Checklist

- [ ] Code follows PEP 8 style
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] Commit messages are descriptive
- [ ] No merge conflicts
- [ ] Changes are focused and not too large

---

## Common Development Tasks

### Adding a New Feature

1. **Create feature branch**:
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Implement feature**:
   ```python
   # Add code to appropriate file
   def new_function():
       """Description of new function."""
       pass
   ```

3. **Write tests**:
   ```python
   def test_new_function():
       """Test new function."""
       result = new_function()
       assert result is not None
   ```

4. **Update documentation**:
   - Update README if user-facing
   - Update API.md if adding endpoints
   - Add docstrings to new functions

5. **Test and commit**:
   ```bash
   pytest
   black .
   git add .
   git commit -m "feat: Add new feature"
   ```

### Updating Dependencies

```bash
# Update single package
pip install --upgrade langchain

# Update all packages
pip install --upgrade -r requirements.txt

# Check for outdated packages
pip list --outdated

# Save updated requirements
pip freeze > requirements.txt
```

### Creating a New Utility Function

```python
# src/utils.py (new file)

from typing import List, Dict

def calculate_similarity_score(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
        
    Returns:
        Similarity score between 0 and 1
        
    Example:
        >>> calculate_similarity_score([1, 0, 0], [1, 0, 0])
        1.0
    """
    import numpy as np
    
    vec1_normalized = np.array(vec1) / np.linalg.norm(vec1)
    vec2_normalized = np.array(vec2) / np.linalg.norm(vec2)
    
    return float(np.dot(vec1_normalized, vec2_normalized))
```

### Database Migration (Future)

When schema changes:

```bash
# Create migration
alembic revision --autogenerate -m "Add user_feedback table"

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

## Performance Optimization

### Profiling

```python
import cProfile
import pstats

# Profile the application
profiler = cProfile.Profile()
profiler.enable()

# Code to profile
result = rag_chain.invoke({"input": "What is diabetes?"})

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slow functions
```

### Caching

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def get_embedding(text: str):
    """Cache embeddings to avoid recomputation."""
    return embeddings.embed_query(text)
```

### Async Requests

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def process_queries_async(queries: List[str]):
    """Process multiple queries concurrently."""
    loop = asyncio.get_event_loop()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = await asyncio.gather(*[
            loop.run_in_executor(executor, rag_chain.invoke, {"input": q})
            for q in queries
        ])
    
    return results
```

---

## Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)

---

## Getting Help

- Check existing [Issues](https://github.com/entbappy/End-to-End-Medical-Chatbot/issues)
- Review [Discussions](https://github.com/entbappy/End-to-End-Medical-Chatbot/discussions)
- Read [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- Check [API.md](API.md) for endpoint documentation
