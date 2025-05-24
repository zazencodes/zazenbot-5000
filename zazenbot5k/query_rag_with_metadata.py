import argparse
import json
import logging
import os
import re

import vertexai
from config import BUCKET_NAME, GCP_LLM_MODEL_ID
from dotenv import load_dotenv
from google.cloud import storage
from query_rag import ask_rag_question
from vertexai.generative_models import GenerativeModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

load_dotenv(override=True)


def get_metadata_from_gcs(title):
    """
    Retrieve metadata JSON file from Google Cloud Storage

    Args:
        title: The title of the document (without extension)

    Returns:
        Dictionary containing the metadata
    """
    logger.info(f"Retrieving metadata for document: {title}")
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    # Strip any extension from the title and use .json extension
    base_title = os.path.splitext(title)[0]
    blob_path = f"yt-rag/info/{base_title}.json"
    logger.info(f"Looking for metadata at path: {blob_path}")

    blob = bucket.blob(blob_path)

    try:
        json_content = blob.download_as_string()
        metadata = json.loads(json_content)
        logger.info(f"Successfully retrieved metadata for {title}")
        return metadata
    except Exception as e:
        logger.error(f"Error retrieving metadata for {title}: {e}")
        return None


def format_enhanced_prompt(question):
    """
    Format an enhanced prompt for the LLM that requests timestamp information

    Args:
        question: The user's original question
        context: The retrieved context from RAG

    Returns:
        Enhanced prompt string
    """
    prompt = f"""
I need you to answer the following question and then follow the instructions below.

Question: {question}

Based on the video transcript of the top RAG content, identify the most relevant timestamp.
This will be available at the start of the paragraph, in HH:MM:SS format, e.g. [00:03:52]

Please respond in JSON format with two fields:
1. "answer": Your comprehensive answer to the question
2. "timestamp": The most relevant timestamp in HH:MM:SS format

If you cannot determine a timestamp, use "00:00:00".
""".strip()
    return prompt


def timestamp_to_seconds(timestamp):
    """
    Convert a timestamp in HH:MM:SS format to seconds for use in URL

    Args:
        timestamp: Timestamp string in HH:MM:SS format

    Returns:
        Total seconds as integer
    """
    # Handle case where timestamp might be missing or invalid
    if not timestamp or timestamp == "00:00:00":
        logger.info("No timestamp provided or default timestamp used")
        return 0

    # Extract timestamp using regex to be more flexible with format
    match = re.search(r"(\d+):(\d+):(\d+)", timestamp)
    if match:
        hours, minutes, seconds = map(int, match.groups())
        total_seconds = hours * 3600 + minutes * 60 + seconds
        logger.info(f"Converted timestamp {timestamp} to {total_seconds} seconds")
        return total_seconds

    logger.warning(f"Failed to parse timestamp format: {timestamp}")
    return 0


def format_response(rag_response, metadata, timestamp):
    """
    Format the final response with RAG response, metadata, and timestamp

    Args:
        rag_response: The parsed answer from the JSON response
        metadata: The metadata dictionary
        timestamp: The timestamp in HH:MM:SS format

    Returns:
        Formatted response string
    """
    logger.info(f"Formatting response with timestamp: {timestamp}")
    formatted_response = f"{rag_response}\n"

    if metadata:
        logger.info(f"Adding metadata to response: {metadata.get('title', 'N/A')}")
        formatted_response += "🍿Source video:\n"
        formatted_response += f"{metadata.get('title', 'N/A')}\n"

        # Add timestamp to the URL if available
        url = metadata.get("url", "N/A")
        if url and "youtu" in url and timestamp and timestamp != "00:00:00":
            # Convert timestamp to seconds for the URL parameter
            seconds = timestamp_to_seconds(timestamp)
            logger.info(f"Adding timestamp {timestamp} ({seconds}s) to URL")
            # Check if URL already has parameters
            if "?" in url:
                url = f"{url}&t={seconds}s"
            else:
                url = f"{url}?t={seconds}s"

        formatted_response += f"{url}"
        if source_code := metadata.get("source_code_url"):
            formatted_response += f"\n\n💾Source Code: {source_code}"
    else:
        logger.warning("No additional metadata found for this content.")

    return formatted_response


def process_question(question: str, persona: str):
    """
    Process a user question through the RAG system and enhance with metadata and timestamp

    Args:
        question: The user's question
        persona: The persona to use for the question

    Returns:
        Enhanced response string
    """
    logger.info(f"Processing question: {question} with persona: {persona}")

    # Get RAG response
    rag_llm_response = get_rag_response(question, persona)

    # Extract context information
    context_title, context_text = extract_context_info(rag_llm_response)

    # Extract timestamp from context using generative model
    timestamp = extract_timestamp_using_llm(context_text, question)
    logger.info(f"Selected timestamp for response: {timestamp}")

    # Get metadata from GCS
    metadata = get_metadata_from_gcs(context_title)

    # Format the final response
    answer = rag_llm_response.text
    formatted_response = format_response(answer, metadata, timestamp)
    logger.info("Response formatting complete")
    return formatted_response


def get_rag_response(question: str, persona: str):
    """
    Send question to RAG system and get response

    Args:
        question: The user's question
        persona: The persona to use for the question

    Returns:
        RAG response object
    """
    logger.info("Sending question to RAG system...")
    rag_llm_response = ask_rag_question(question, persona)
    logger.info(f"Received RAG response:\n{rag_llm_response}")
    return rag_llm_response


def extract_context_info(rag_llm_response):
    """
    Extract title and text from the top context in RAG response

    Args:
        rag_llm_response: Response from RAG system

    Returns:
        Tuple of (context_title, context_text)
    """
    try:
        top_context = rag_llm_response.candidates[
            0
        ].grounding_metadata.grounding_chunks[0]
        context_title = top_context.retrieved_context.title
        context_text = top_context.retrieved_context.text
        logger.info(f"Top context source: {context_title}")
    except (IndexError, AttributeError) as e:
        logger.warning(f"Failed to extract RAG context match: {e}")
        context_title = "unknown"
        context_text = "unknown"

    return context_title, context_text


def extract_timestamp_using_llm(context_text, question):
    """
    Extract the most relevant timestamp from context text using a generative model

    Args:
        context_text: The text content from RAG context
        question: The user's original question

    Returns:
        Timestamp string in HH:MM:SS format
    """
    # First check if there are any timestamps in the context
    all_timestamps = re.findall(r"\[(\d{2}:\d{2}:\d{2})\]", context_text)

    if not all_timestamps:
        logger.warning("No timestamps found in context, using 00:00:00")
        return "00:00:00"

    if len(all_timestamps) == 1:
        logger.info(f"Only one timestamp found in context: {all_timestamps[0]}")
        return all_timestamps[0]

    # Multiple timestamps found, use generative model to select the most relevant one
    logger.info(
        f"Found {len(all_timestamps)} timestamps in context, using generative model to select the most relevant one"
    )

    try:
        # Initialize Vertex AI
        vertexai.init()

        # Create the model
        model = GenerativeModel(GCP_LLM_MODEL_ID)

        # Create prompt for the model
        prompt = f"""
        I have a question and a transcript with multiple timestamps. Please identify the most relevant timestamp
        that best answers the question.

        Question: {question}

        Transcript:
        {context_text}

        Please respond with ONLY the most relevant timestamp in HH:MM:SS format (e.g., "00:03:45").
        If you cannot determine a relevant timestamp, respond with "00:00:00".
        """

        logger.info(
            f"Sending request to generative model to select timestamp:\n{prompt}"
        )
        response = model.generate_content(prompt)
        logger.info(f"Response from model for timestamp request:\n{response}")

        # Extract timestamp from response
        response_text = response.text.strip()
        timestamp_match = re.search(r"(\d{2}:\d{2}:\d{2})", response_text)

        if timestamp_match:
            selected_timestamp = timestamp_match.group(1)
            logger.info(f"Generative model selected timestamp: {selected_timestamp}")

            # Verify the selected timestamp exists in the original context
            if selected_timestamp in all_timestamps:
                return selected_timestamp
            else:
                logger.warning(
                    f"Selected timestamp {selected_timestamp} not found in original context, using first timestamp"
                )
                return all_timestamps[0]
        else:
            logger.warning(
                "Generative model did not return a valid timestamp, using first timestamp"
            )
            return all_timestamps[0]

    except Exception as e:
        logger.error(f"Error using generative model to select timestamp: {e}")
        logger.warning("Falling back to first timestamp in context")
        return all_timestamps[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Ask a question to the RAG-enabled Gemini model with enhanced metadata and timestamps"
    )
    parser.add_argument("question", type=str, help="The question to ask")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--persona",
        type=str,
        choices=[
            "politician",
            "wannabe-influencer",
            "robot-with-exitential-crisis",
        ],
        help="The persona to use for the question",
    )

    args = parser.parse_args()

    # Set debug level if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")

    logger.info(f"Starting query process with question: {args.question}")
    enhanced_response = process_question(args.question, args.persona)
    logger.info("Query processing complete, printing response\n")
    print(enhanced_response)
