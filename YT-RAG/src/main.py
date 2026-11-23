# import sys
# from src.ingest import fetch_youtube_transcript, split_transcript_into_chunks
# from src.vectorstore import create_vector_store, get_retriever
# from src.rag_chain import build_rag_chain


# def main():
#     video_id = "Gfr50f6ZBvo"  # Replace or accept as user input
    
#     print(f"Fetching transcript for video: {video_id}...")
#     try:
#         transcript = fetch_youtube_transcript(video_id)
#     except Exception as e:
#         print(f"Error: {e}")
#         sys.exit(1)

#     print("Splitting transcript into chunks...")
#     chunks = split_transcript_into_chunks(transcript)
#     print(f"Total chunks created: {len(chunks)}")

#     print("Generating embeddings & setting up FAISS vector store...")
#     vector_store = create_vector_store(chunks)
#     retriever = get_retriever(vector_store)

#     print("Building RAG Chain...")
#     rag_chain = build_rag_chain(retriever)

#     # Interactive Query Loop
#     print("\n--- YouTube Transcript RAG System Ready ---")
#     while True:
#         query = input("\nAsk a question (or type 'exit' to quit): ")
#         if query.strip().lower() in ['exit', 'quit']:
#             break

#         print("\nThinking...")
#         response = rag_chain.invoke(query)
#         print(f"\nAnswer:\n{response}")


# if __name__ == "__main__":
#     main()




import warnings
warnings.filterwarnings("ignore")

import sys
from src.ingest import extract_video_id, fetch_youtube_transcript, split_transcript_into_chunks
from src.vectorstore import create_vector_store, get_retriever
from src.rag_chain import build_rag_chain


def main():
    print("--- YouTube Transcript RAG System ---")
    
    # Interactive input for YouTube URL or ID
    url_input = input("\nEnter YouTube Video URL or Video ID: ").strip()
    if not url_input:
        print("Error: Input cannot be empty.")
        sys.exit(1)

    try:
        video_id = extract_video_id(url_input)
        print(f"\nExtracted Video ID: {video_id}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Fetching transcript for video ID: {video_id}...")
    try:
        transcript = fetch_youtube_transcript(video_id)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("Splitting transcript into chunks...")
    chunks = split_transcript_into_chunks(transcript)
    print(f"Total chunks created: {len(chunks)}")

    print("Generating embeddings & setting up FAISS vector store...")
    vector_store = create_vector_store(chunks)
    retriever = get_retriever(vector_store)

    print("Building RAG Chain...")
    rag_chain = build_rag_chain(retriever)

    print("\n--- System Ready for Questions ---")
    while True:
        query = input("\nAsk a question (or type 'exit' to quit): ")
        if query.strip().lower() in ['exit', 'quit']:
            print("Exiting...")
            break

        print("\nThinking...")
        response = rag_chain.invoke(query)
        print(f"\nAnswer:\n{response}")


if __name__ == "__main__":
    main()