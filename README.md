# ZazBot 5000

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
python zazenbot5k/update_gcs_from_local.py # Upload local files (has CLI arg for uploading just one)
python zazenbot5k/create_rag_corpus.py # Create RAG corpus (only run this once)
# python zazenbot5k/delete_rag_corpus.py # To delete it
python zazenbot5k/upload_rag_corpus_files.py # Update with new files in cloud storage (will only process new files)
```

3. Ask a question

```bash
python zazenbot5k/query_rag.py "How do you use ollama with the llm cli?"
python zazenbot5k/query_rag_with_metadata.py "explain agents" # Include metadata lookup and provide as context in answer
python zazenbot5k/query_rag_with_metadata.py "explain agents" # Include metadata lookup and provide as context in answer
```

