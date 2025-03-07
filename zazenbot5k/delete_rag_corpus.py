import os

import vertexai
from config import CORPUS_NAME
from dotenv import load_dotenv
from vertexai.preview import rag

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location=LOCATION)

res = rag.delete_corpus(name=CORPUS_NAME)

print("Corpus delted:", CORPUS_NAME)
