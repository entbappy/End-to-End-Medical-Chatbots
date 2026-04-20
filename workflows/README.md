# System Workflows

This folder contains visual flowcharts and diagrams representing different workflows and data flows in the Medical Chatbot system.

## Files

- **data_flow.mmd** - Overall data flow from documents to user responses
- **rag_pipeline.mmd** - Detailed RAG pipeline process
- **user_query_flow.mmd** - User query processing from input to response
- **deployment_pipeline.mmd** - CI/CD deployment workflow

## Viewing Diagrams

### Option 1: GitHub (Automatic)
If these files are on GitHub, they will render automatically in the repository view.

### Option 2: Mermaid Live Editor
Go to [mermaid.live](https://mermaid.live/) and paste the diagram content.

### Option 3: VS Code
Install "Markdown Preview Mermaid Support" extension for VS Code preview.

### Option 4: Command Line
```bash
# Using mermaid-cli
npm install -g @mermaid-js/mermaid-cli
mmdc -i data_flow.mmd -o data_flow.svg
```

## Quick Diagrams Overview

### Data Flow
Shows how medical PDFs flow through the system to become stored vectors in Pinecone.

### RAG Pipeline
Illustrates the complete Retrieval-Augmented Generation process for answering user queries.

### User Query Flow
Details the step-by-step process when a user submits a medical question.

### Deployment Pipeline
Shows the CI/CD workflow from code push to production deployment on AWS.
