# from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from src.config import CHUNK_SIZE, CHUNK_OVERLAP


# def fetch_youtube_transcript(video_id: str) -> str:
#     """Fetches YouTube transcript for a given video ID using updated youtube-transcript-api."""
#     try:
#         # Create an instance and call fetch
#         api = YouTubeTranscriptApi()
#         transcript_data = api.fetch(video_id, languages=["en"])
        
#         # Extract text snippets
#         transcript = " ".join([chunk.text if hasattr(chunk, 'text') else chunk['text'] for chunk in transcript_data])
#         return transcript
#     except TranscriptsDisabled:
#         raise ValueError(f"No captions/transcripts available for video ID: {video_id}")
#     except Exception as e:
#         # Fallback in case of legacy version format
#         try:
#             transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
#             return " ".join([chunk["text"] for chunk in transcript_list])
#         except Exception:
#             raise RuntimeError(f"An error occurred while fetching the transcript: {e}")


# def split_transcript_into_chunks(transcript: str):
#     """Splits text transcript into chunked LangChain Document objects."""
#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=CHUNK_SIZE,
#         chunk_overlap=CHUNK_OVERLAP
#     )
#     chunks = splitter.create_documents([transcript])
#     return chunks


from urllib.parse import parse_qs, urlparse
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import CHUNK_SIZE, CHUNK_OVERLAP


def extract_video_id(url_or_id: str) -> str:
    """Extracts the 11-character YouTube video ID from various URL formats or raw ID string."""
    url_or_id = url_or_id.strip()

    # If user provided a direct 11-char ID without slashes or query params
    if len(url_or_id) == 11 and "/" not in url_or_id and "?" not in url_or_id:
        return url_or_id

    parsed_url = urlparse(url_or_id)

    # Handles standard URLs like: https://www.youtube.com/watch?v=VIDEO_ID
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            query_params = parse_qs(parsed_url.query)
            if "v" in query_params:
                return query_params["v"][0]
        # Handles YouTube Shorts: https://www.youtube.com/shorts/VIDEO_ID
        elif parsed_url.path.startswith("/shorts/"):
            return parsed_url.path.split("/")[2]

    # Handles short links like: https://youtu.be/VIDEO_ID
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.lstrip("/")

    raise ValueError(f"Could not extract a valid YouTube Video ID from input: '{url_or_id}'")


def fetch_youtube_transcript(video_id: str) -> str:
    """Fetches YouTube transcript for a given video ID."""
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=["en"])
        return " ".join([chunk.text if hasattr(chunk, 'text') else chunk['text'] for chunk in transcript_data])
    except TranscriptsDisabled:
        raise ValueError(f"No captions/transcripts available for video ID: {video_id}")
    except Exception as e:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
            return " ".join([chunk["text"] for chunk in transcript_list])
        except Exception:
            raise RuntimeError(f"An error occurred while fetching the transcript: {e}")


def split_transcript_into_chunks(transcript: str):
    """Splits text transcript into chunked LangChain Document objects."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    return splitter.create_documents([transcript])