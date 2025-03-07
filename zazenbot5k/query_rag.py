import argparse
import os

import vertexai
from config import CORPUS_NAME, GCP_LLM_MODEL_ID
from dotenv import load_dotenv
from vertexai.preview import rag
from vertexai.preview.generative_models import GenerativeModel, Tool

load_dotenv(override=True)

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
LOCATION = os.getenv("GCP_LOCATION")


def ask_rag_question(question: str):
    """
    Ask a question to the RAG-enabled Gemini model

    Args:
        question: The question to ask

    Returns:
        The model's response object
    """

    # Initialize Vertex AI API once per session
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    rag_retrieval_tool = Tool.from_retrieval(
        retrieval=rag.Retrieval(
            source=rag.VertexRagStore(
                rag_resources=[
                    rag.RagResource(
                        rag_corpus=CORPUS_NAME,
                    )
                ],
                similarity_top_k=3,
                # vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD,
            ),
        )
    )

    rag_model = GenerativeModel(
        model_name=GCP_LLM_MODEL_ID,
        tools=[rag_retrieval_tool],
    )
    response = rag_model.generate_content(question)
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ask a question to the RAG-enabled Gemini model"
    )
    parser.add_argument("question", type=str, help="The question to ask")

    args = parser.parse_args()

    response = ask_rag_question(args.question)
    print("FULL RESPONSE:")
    print(response)

    print()
    print("RESPONSE TEXT:")
    print(response.text)

    print()
    print("TOP CONTEXT:")
    print(response.candidates[0].grounding_metadata.grounding_chunks[0])
