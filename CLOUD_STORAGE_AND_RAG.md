# Data Ingestion Guide: Local Storage to GCS & RAG DB

This guide outlines the process of migrating local planning documents (`local_storage/`) to Google Cloud Storage (GCS) and ingesting them into a Retrieval-Augmented Generation (RAG) database for LLM analysis.

---

## Phase 1: Uploading to Google Cloud Storage (GCS)

### 1. Prerequisites
- **GCP Project**: A Google Cloud Platform project with the Storage API enabled.
- **Bucket**: A GCS bucket (e.g., `innsight-data-storage`).
- **Authentication**: A Service Account key JSON file with `Storage Object Admin` permissions. Set the environment variable:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account-file.json"
  ```

### 2. Upload Script
Install the client library: `pip install google-cloud-storage`

```python
import os
from google.cloud import storage

def upload_to_gcs(local_dir, bucket_name, gcs_prefix=""):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_file_path = os.path.join(root, file)
            # Create the relative path for GCS (maintaining folder structure)
            relative_path = os.path.relpath(local_file_path, local_dir)
            blob_path = os.path.join(gcs_prefix, relative_path)
            
            blob = bucket.blob(blob_path)
            print(f"Uploading {local_file_path} -> gs://{bucket_name}/{blob_path}")
            blob.upload_from_filename(local_file_path)

if __name__ == "__main__":
    upload_to_gcs('local_storage', 'your-bucket-name', 'taba_docs')
```

---

## Phase 2: Ingesting into a RAG Database

To make the Hebrew PDF documents searchable by an LLM (like Gemini or GPT-4), they must be processed into a Vector Database.

### 1. Recommended Stack
- **PDF Extraction**: `pdfplumber` or `PyMuPDF` (Better for Hebrew than PyPDF2).
- **Orchestration**: `LangChain` or `LlamaIndex`.
- **Embeddings**: `text-embedding-004` (Google) or `text-embedding-3-large` (OpenAI). Both have excellent Hebrew support.
- **Vector Store**: `ChromaDB` (Local testing), `Pinecone` (Cloud), or `Vertex AI Vector Search`.

### 2. RAG Pipeline Implementation
Install requirements:
```bash
pip install langchain langchain-google-genai pdfplumber chromadb
```

```python
import os
from langchain_community.document_loaders import DirectoryLoader, PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

def create_rag_db():
    # 1. Load PDFs (Using PDFPlumber for better Hebrew extraction)
    print("Loading documents...")
    loader = DirectoryLoader(
        "local_storage/", 
        glob="./**/*.pdf", 
        loader_cls=PDFPlumberLoader
    )
    documents = loader.load()

    # 2. Chunking (Small chunks are better for precise retrieval)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")

    # 3. Embedding and Storage
    # Set GOOGLE_API_KEY environment variable
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    print("Creating Vector DB...")
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./vector_db"
    )
    print("Database ready at ./vector_db")

if __name__ == "__main__":
    create_rag_db()
```

---

## Advanced: Google Cloud Native Approach (Vertex AI Search)

For production-grade RAG, using **Vertex AI Search** (formerly Enterprise Search) is highly recommended. It eliminates the need to manage vector databases, chunking logic, and complex OCR for Hebrew planning maps.

### 1. Why use Vertex AI Search for Hebrew Plans?
- **Built-in OCR**: Automatically extracts text from complex PDFs, maps, and tables.
- **Managed RAG**: Handles chunking, embedding, and vector storage internally.
- **Grounding**: Can be directly connected to Gemini for "grounded" answers based ONLY on your planning docs.

### 2. Setup Steps
1.  **Console Setup**: Go to [Vertex AI Search & Conversation](https://console.cloud.google.com/gen-app-builder) in the GCP Console.
2.  **Create Data Store**: 
    - Choose **Cloud Storage** as the source.
    - Point it to your bucket: `gs://your-bucket-name/taba_docs/`.
    - Select "Unstructured documents" and enable **OCR** if your PDFs are scans.
    - **Name**: `taba-plans-datastore`
3.  **Create App**: 
    - Create a new **Search** app.
    - **Name**: `innsight-search-app`
    - Connect it to the `taba-plans-datastore` you just created.
    - Note the **Data Store ID** (found in the Data Store details page).

### 3. Querying the Data Store (Python)
Install the client: `pip install google-cloud-discoveryengine`

```python
from google.cloud import discoveryengine_v1beta as discoveryengine

def search_plans(project_id, location, data_store_id, search_query):
    # data_store_id will be the ID associated with 'taba-plans-datastore'
    client = discoveryengine.SearchServiceClient()

    # The full resource name of the search engine serving config
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_config",
    )

    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=5,
    )

    response = client.search(request)
    
    for result in response.results:
        print(f"Document Found: {result.document.derived_struct_data['title']}")
        # Snippets contain the relevant text found for RAG
        snippets = result.document.derived_struct_data.get('snippets', [])
        for snippet in snippets:
            print(f"Snippet: {snippet.get('snippet')}")

if __name__ == "__main__":
    search_plans(
        project_id="your-project-id",
        location="global",
        data_store_id="your-data-store-id",
        search_query="תוכניות לבינוי מלונות בתל אביב"
    )
```

### 4. Integration with Gemini
You can use the **Vertex AI SDK** to ask Gemini questions grounded in this search data:

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Tool, google_search_retrieval

vertexai.init(project="your-project-id", location="us-central1")

# Define the search tool pointing to your data store
datastore_tool = Tool.from_retrieval(
    retrieval=discoveryengine.Retrieval(
        source=discoveryengine.VertexAISearch(
            datastore=f"projects/your-project-id/locations/global/collections/default_collection/dataStores/your-data-store-id"
        )
    )
)

model = GenerativeModel("gemini-1.5-flash")
response = model.generate_content(
    "Are there any new hotel plans in Jerusalem?",
    tools=[datastore_tool]
)

print(response.text)
```

## Hebrew Language Considerations
- **Right-to-Left (RTL)**: When extracting text locally, `pdfplumber` handles RTL logic better than standard libraries.
- **Encoding**: Always ensure you use `utf-8` when reading/writing any extracted text files.
- **Context**: Israeli planning documents often contain large tables and maps. For these, a **Multimodal RAG** (sending image snapshots of pages to Gemini 1.5 Pro) often yields better results than text extraction alone.
