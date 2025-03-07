import os

import vertexai
from dotenv import load_dotenv
from vertexai.preview import rag

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")

# Initialize Vertex AI API once per session
vertexai.init(project=PROJECT_ID, location=LOCATION)

corpus = rag.create_corpus(
    display_name="zazenbot-5000-video-transcripts",
    description="Transcripts and other metadata for ZazenCodes YouTube videos",
)
print("Created corpus:", corpus)

# This ran for about 2 minutes
# Output:
# Created corpus: RagCorpus(name='projects/890511813715/locations/us-central1/ragCorpora/2305843009213693952', display_name='zazenbot-5000-video-transcripts', description='Transcripts and other metadata for ZazenCodes YouTube videos', backend_config=RagVectorDbConfig(vector_db=None, rag_embedding_model_config=RagEmbeddingModelConfig(vertex_prediction_endpoint=VertexPredictionEndpoint(endpoint=None, publisher_model='projects/890511813715/locations/us-central1/publishers/google/models/text-embedding-005', model=None, model_version_id=None))))
