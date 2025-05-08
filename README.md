# ZazenBot 5000

## API Usage

The ZazenBot 5000 can be run as a FastAPI application, either directly or using Docker. The API provides endpoints for querying the RAG system with metadata.

### Running with Docker

1. Set up your environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your GCP project details
   ```

2. Place your Google Cloud credentials JSON file in the `credentials` directory:
   ```bash
   # The file should be named google-credentials.json
   mkdir -p credentials
   # Copy your credentials file to credentials/google-credentials.json
   ```

3. Build and start the Docker container:
   ```bash
   docker-compose up -d
   ```

4. The API will be available at http://localhost:8000
   - Health check: GET http://localhost:8000/health
   - Query endpoint: POST http://localhost:8000/query

5. Example queries:

   Using curl:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question": "explain agents"}'
   ```

   Using the provided Python script:
   ```bash
   python test_api.py "explain agents"
   ```

### Testing the API Locally

You can test the ZazenBot API locally using curl commands. Here are some examples:

1. **Health Check**:
   ```bash
   curl http://localhost:8000/health
   ```
   Expected response: `{"status":"healthy"}`

2. **Query the RAG System**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"What is RAG?"}'
   ```

3. **Testing with Complex Queries**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"Explain the differences between agents and assistants in AI"}'
   ```

4. **Saving Response to a File**:
   ```bash
   curl -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"Give me tips for data engineering"}'
     -o response.txt
   ```

5. **Verbose Output for Debugging**:
   ```bash
   curl -v -X POST http://localhost:8000/query \
     -H "Content-Type: application/json" \
     -d '{"question":"What are some Neovim plugins?"}'
   ```

The API returns plain text responses that include the answer to your question enhanced with metadata from the RAG system.

### Running Directly

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn
   ```

2. Run the FastAPI application:
   ```bash
   cd zazenbot5k
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

## Add new video

1. Create folder in `yt-video-metadata`, e.g.

```plaintext
yt-video-metadata/2025_01_08_finally_figured_out_what_to_do
├── info.json
├── summary.md
├── transcript_text.txt
└── transcript_markers.txt
```

Use GPT for summary and info (see [notion SOP](https://www.notion.so/cotillion19/Generate-summary-SOP-1ae52790491144299906782b5cf38336) for prompts)

2. Create and populate rag corpus

```bash
# Upload local files (has CLI arg for uploading just one)
python zazenbot5k/update_gcs_from_local.py

# Create RAG corpus (only run this once)
python zazenbot5k/create_rag_corpus.py

# To delete it
# python zazenbot5k/delete_rag_corpus.py

# Update with new files in cloud storage (will only process new files)
python zazenbot5k/upload_rag_corpus_files.py
```

3. Ask a question

```bash
# Just ask a basic question using RAG
venv/bin/python zazenbot5k/query_rag.py "Give me a bunch of data engineering hacks for Neovim."

# Include metadata lookup and provide as context in answer
venv/bin/python zazenbot5k/query_rag_with_metadata.py "explain agents"
```

