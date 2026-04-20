# Installation & Setup Guide

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Docker Setup](#docker-setup)

---

## Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 4GB RAM (8GB+ recommended)
- **Disk Space**: 5GB for dependencies and data
- **Internet**: Required for API calls and model downloads

### Required Software

1. **Git** (for cloning repository)
   ```bash
   git --version  # Should output version info
   ```

2. **Python 3.10 or higher**
   ```bash
   python --version  # Should show Python 3.10+
   ```

3. **API Keys** (create free accounts)
   - [OpenAI API Key](https://platform.openai.com/account/api-keys)
   - [Pinecone API Key](https://www.pinecone.io/)

### Optional Software

- **Conda/Mamba**: For environment management (recommended)
- **UV**: For faster dependency installation (~10x faster)
- **Docker**: For containerized deployment

---

## Installation Methods

### Method 1: Conda (Recommended for ML/Data Scientists)

Conda is widely used in the data science community and handles complex dependencies well.

#### Step 1: Clone Repository

```bash
git clone https://github.com/entbappy/End-to-End-Medical-Chatbot.git
cd End-to-End-Medical-Chatbot
```

#### Step 2: Create Conda Environment

```bash
# Create environment with Python 3.10
conda create -n medibot python=3.10 -y

# Activate environment
conda activate medibot
```

**Verify Activation**:
```bash
which python  # Should show path to conda python
python --version  # Should show 3.10.x
```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed langchain-0.3.26 flask-3.1.1 sentence-transformers-4.1.0 ...
```

**Verify Installation**:
```bash
python -c "import langchain; print(langchain.__version__)"
# Should output: 0.3.26
```

#### Step 4: Configure Environment Variables

Create `.env` file in root directory:

```bash
# Create .env file
cat > .env << EOF
PINECONE_API_KEY="your_pinecone_key_here"
OPENAI_API_KEY="your_openai_key_here"
EOF
```

Or manually create the file and add:
```ini
PINECONE_API_KEY=your_pinecone_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Never commit `.env` to version control!

#### Step 5: Prepare Data

Place your medical PDF files in the `data/` directory:

```bash
# Create data directory if it doesn't exist
mkdir -p data/

# Add your PDFs
cp /path/to/medical/documents/*.pdf data/
```

#### Step 6: Index Data to Pinecone

```bash
python store_index.py
```

**Expected Output**:
```
Loading PDFs...
Loaded 5 documents
Splitting text...
Created 150 text chunks
Generating embeddings...
Uploading to Pinecone...
✓ Successfully indexed to Pinecone!
```

**What Happens**:
- Loads all PDFs from `data/` directory
- Splits text into chunks (500 chars, 20 char overlap)
- Generates embeddings using HuggingFace model
- Uploads to Pinecone index `medical-chatbot`

#### Step 7: Run Application

```bash
python app.py
```

**Expected Output**:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:8080
```

**Access Application**:
Open browser and navigate to: `http://localhost:8080`

---

### Method 2: UV (Faster Alternative)

UV provides ~10x faster dependency resolution and is ideal for CI/CD pipelines.

#### Step 1: Install UV

**macOS/Linux**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (using PowerShell):
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify Installation**:
```bash
uv --version  # Should output version info
```

#### Step 2: Clone Repository

```bash
git clone https://github.com/entbappy/End-to-End-Medical-Chatbot.git
cd End-to-End-Medical-Chatbot
```

#### Step 3: Create Virtual Environment

```bash
# Create Python 3.10 environment
uv venv --python 3.10 .venv

# Activate environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

**Verify Activation**:
```bash
which python  # Should show .venv/bin/python
python --version  # Should show 3.10.x
```

#### Step 4: Install Dependencies

```bash
# UV install is ~10x faster than pip
uv pip install -r requirements.txt
```

#### Steps 5-7: Environment, Data, and Run

Same as Conda method above (Steps 4-7).

---

### Method 3: Virtual Environment (Standard Python)

For those who prefer standard Python tools.

#### Step 1-2: Clone and Navigate

```bash
git clone https://github.com/entbappy/End-to-End-Medical-Chatbot.git
cd End-to-End-Medical-Chatbot
```

#### Step 3: Create Virtual Environment

**macOS/Linux**:
```bash
python3.10 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
python -m venv venv
venv\Scripts\activate
```

#### Step 4: Upgrade pip

```bash
python -m pip install --upgrade pip
```

#### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Steps 6-8: Environment, Data, and Run

Same as Conda method above (Steps 4-7).

---

## Environment Configuration

### API Keys Setup

#### OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (you won't see it again!)
5. Add to `.env`:
   ```ini
   OPENAI_API_KEY=sk_test_xxxxxxxxxxxxx
   ```

#### Pinecone API Key

1. Go to [Pinecone Console](https://www.pinecone.io/)
2. Sign in or create account
3. Go to "API Keys" section
4. Copy your API key
5. Add to `.env`:
   ```ini
   PINECONE_API_KEY=pcn_xxxxxxxxxxxxx
   ```

### .env File Best Practices

```ini
# ✅ Good format
OPENAI_API_KEY=sk_test_xxxxxxxxxxxxx
PINECONE_API_KEY=pcn_xxxxxxxxxxxxx

# ❌ Avoid these
OPENAI_API_KEY = "sk_test_xxxxxxxxxxxxx"  # Extra spaces/quotes
PINECONE_API_KEY='pcn_xxxxxxxxxxxxx'      # Single quotes
MY_KEYS=sk_test_xxxxxxxxxxxxx:pcn_xxxxx   # Multiple in one var
```

### Verify Configuration

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OPENAI_API_KEY:', 'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set')
print('PINECONE_API_KEY:', 'Set' if os.environ.get('PINECONE_API_KEY') else 'Not set')
"
```

---

## Database Setup

### Pinecone Index Creation

The application expects an index named `medical-chatbot`. When you run `store_index.py`, it will:

1. Check if index exists
2. Create if doesn't exist
3. Upsert embeddings

### Understanding Vector Dimensions

- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Vector Dimension**: 384
- **Metric**: Cosine Similarity
- **Index Name**: `medical-chatbot`

```python
# This is handled automatically by store_index.py
embeddings = download_hugging_face_embeddings()  # Returns 384-dim vectors
```

### Data Format

When indexing documents, each vector is stored with metadata:

```python
{
    "id": "doc_001",
    "values": [0.123, 0.456, ...],  # 384 dimensions
    "metadata": {
        "source": "data/medical_guide.pdf",
        "page": 1,
        "chunk": 0
    }
}
```

---

## Verification

### Verify All Components

Run this script to verify everything is set up correctly:

```bash
python << 'EOF'
import os
import sys
from dotenv import load_dotenv

print("=" * 50)
print("MEDICAL CHATBOT SETUP VERIFICATION")
print("=" * 50)

# Check Python version
print(f"\n✓ Python Version: {sys.version.split()[0]}")

# Check environment variables
load_dotenv()
print(f"✓ OPENAI_API_KEY: {'Set' if os.environ.get('OPENAI_API_KEY') else '❌ Not set'}")
print(f"✓ PINECONE_API_KEY: {'Set' if os.environ.get('PINECONE_API_KEY') else '❌ Not set'}")

# Check imports
try:
    import flask
    print(f"✓ Flask: {flask.__version__}")
except ImportError:
    print("❌ Flask not installed")

try:
    import langchain
    print(f"✓ LangChain: {langchain.__version__}")
except ImportError:
    print("❌ LangChain not installed")

try:
    from sentence_transformers import SentenceTransformer
    print(f"✓ Sentence Transformers: Available")
except ImportError:
    print("❌ Sentence Transformers not installed")

# Check data directory
if os.path.exists('data/'):
    pdf_count = len([f for f in os.listdir('data/') if f.endswith('.pdf')])
    print(f"✓ Data Directory: {pdf_count} PDFs found")
else:
    print("❌ Data directory not found")

print("\n" + "=" * 50)
print("SETUP VERIFICATION COMPLETE")
print("=" * 50)
EOF
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "ModuleNotFoundError: No module named 'langchain'"

**Problem**: Dependency not installed

**Solutions**:
```bash
# Verify environment is activated
which python  # Should show venv/conda path

# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt

# Or update pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### 2. "OPENAI_API_KEY not found"

**Problem**: Environment variables not loaded

**Solutions**:
```bash
# Verify .env file exists
ls -la .env  # Should show the file

# Check file contents
cat .env  # Should show your keys (careful!)

# Reinstall python-dotenv
pip install --force-reinstall python-dotenv

# Verify in Python
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('Keys loaded:', bool(os.environ.get('OPENAI_API_KEY')))"
```

#### 3. "Connection error to Pinecone"

**Problem**: API key invalid or network issue

**Solutions**:
```bash
# Verify API key format
echo $PINECONE_API_KEY  # Should show your key

# Test network connectivity
curl https://api.pinecone.io/

# Check Pinecone dashboard for key validity
# https://www.pinecone.io/
```

#### 4. "PDF files not loading"

**Problem**: Data directory empty or wrong location

**Solutions**:
```bash
# Check data directory
ls -la data/  # Should show .pdf files

# Verify PDF files are readable
file data/your_file.pdf  # Should show "PDF document"

# Try a different PDF if first one is corrupted
```

#### 5. "CUDA/GPU issues"

**Problem**: GPU not available (non-critical, will use CPU)

**Solutions**:
```bash
# GPU is optional - CPU will work fine
# If you want GPU support, install CUDA-specific versions
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### 6. "Port 8080 already in use"

**Problem**: Another application using port 8080

**Solutions**:
```bash
# Find process using port 8080
lsof -i :8080  # macOS/Linux

# Kill the process
kill -9 <PID>

# Or use a different port
# Edit app.py: app.run(port=8081)
```

#### 7. "Memory error during embedding generation"

**Problem**: Large PDFs or insufficient RAM

**Solutions**:
```bash
# Use smaller PDFs first
# Reduce chunk size in store_index.py:
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=250, chunk_overlap=10)

# Or increase system memory/swap
```

---

## Docker Setup

### Build Docker Image

```bash
# Build image
docker build -t medical-chatbot:latest .

# Verify image
docker images | grep medical-chatbot
```

### Run Docker Container

```bash
# Create .env file first
cat > .env << EOF
OPENAI_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
EOF

# Run container
docker run -p 8080:8080 \
  --env-file .env \
  -v $(pwd)/data:/app/data \
  medical-chatbot:latest
```

### Docker Compose (Optional)

```yaml
# docker-compose.yml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
    volumes:
      - ./data:/app/data
```

Run with:
```bash
docker-compose up --build
```

---

## Performance Tips

1. **Faster Installation**: Use UV instead of pip
2. **Faster Embeddings**: Use GPU if available
3. **Caching**: Enable Redis for frequently asked questions
4. **Concurrent Requests**: Use production WSGI server:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8080 app:app
   ```

---

## Next Steps

1. ✅ Complete installation
2. ✅ Configure API keys
3. ✅ Add medical PDFs to `data/`
4. ✅ Run `python store_index.py`
5. ✅ Start application with `python app.py`
6. 📖 Read [ARCHITECTURE.md](ARCHITECTURE.md) for system details
7. 📖 Read [API.md](API.md) for endpoint documentation

---

## Getting Help

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [ARCHITECTURE.md](ARCHITECTURE.md) for system details
3. Check logs: `tail -f app.log` (if logging is enabled)
4. Open GitHub issue with:
   - Python version
   - Operating system
   - Error message
   - Steps to reproduce
