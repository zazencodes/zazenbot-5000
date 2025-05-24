import argparse
from pathlib import Path

from config import BUCKET_NAME
from dotenv import load_dotenv
from google.cloud import storage

load_dotenv(override=True)

BUCKET_OUTPUT_DIR = Path("yt-rag")
# INPUT_DIR = Path("yt-vieo-metadata")
INPUT_DIR = Path("/Users/alex/pro/zazencodes-content/videos")


def upload_to_gcs(storage_client, bucket_name, local_path_name: str, blob_name: str):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    print(f"Uploading {blob_name}")
    blob.upload_from_filename(local_path_name)


def process_folder(folder_path: Path, storage_client):
    upload_to_gcs(
        storage_client,
        BUCKET_NAME,
        str(folder_path / "info.json"),
        str(BUCKET_OUTPUT_DIR / "info" / folder_path.name) + ".json",
    )
    upload_to_gcs(
        storage_client,
        BUCKET_NAME,
        str(folder_path / "summary.md"),
        str(BUCKET_OUTPUT_DIR / "summary" / folder_path.name) + ".md",
    )
    upload_to_gcs(
        storage_client,
        BUCKET_NAME,
        folder_path / "transcript_text.txt",
        str(BUCKET_OUTPUT_DIR / "transcript-text" / folder_path.name) + ".txt",
    )
    upload_to_gcs(
        storage_client,
        BUCKET_NAME,
        folder_path / "transcript_markers.txt",
        str(BUCKET_OUTPUT_DIR / "transcript-markers" / folder_path.name) + ".txt",
    )


def main():
    parser = argparse.ArgumentParser(description="Process YouTube metadata folders.")
    parser.add_argument(
        "--folder",
        type=str,
        default=None,
        help="Exact name of the folder to process. If not provided, all folders will be processed.",
    )
    args = parser.parse_args()

    storage_client = storage.Client()

    folders = (
        [INPUT_DIR / args.folder]
        if args.folder
        else [f for f in INPUT_DIR.iterdir() if f.is_dir()]
    )

    for folder in folders:
        if not folder.is_dir():
            print(f"Skipping {folder} (not a directory)")
            continue
        print(f"Processing {folder.name}")
        process_folder(folder, storage_client)


if __name__ == "__main__":
    main()
