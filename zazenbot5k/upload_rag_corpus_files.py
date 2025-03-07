import os

import vertexai
from config import BUCKET_NAME, CORPUS_NAME, RAG_CHUNK_OVERLAP, RAG_CHUNK_SIZE
from dotenv import load_dotenv
from vertexai.preview import rag
from vertexai.preview.rag.utils.resources import ChunkingConfig, TransformationConfig

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")
PATHS = [f"gs://{BUCKET_NAME}/yt-rag/transcript-markers"]
# MAX_EMBEDDING_REQUESTS_PER_MIN = 900

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location=LOCATION)

transformation_config = TransformationConfig(
    chunking_config=ChunkingConfig(
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    ),
)

response = rag.import_files(
    corpus_name=CORPUS_NAME,
    paths=PATHS,
    transformation_config=transformation_config,
)

print(f"Imported {response.imported_rag_files_count} files.")
