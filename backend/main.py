from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import List, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from xhtml2pdf import pisa
from PIL import Image
from io import BytesIO
import fitz
import re
import math
import base64
import os
import json
import html
import urllib.request
from urllib.parse import quote

from yt_dlp import YoutubeDL
from dotenv import load_dotenv

try:
    from youtube_transcript_api.proxies import GenericProxyConfig
except Exception:
    GenericProxyConfig = None

load_dotenv()

app = FastAPI(
    title="Transcribai API",
    description="YouTube Transcript to Excerpts SaaS API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Groq API Key
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TRANSCRIPT_PROXY_URL = os.getenv("TRANSCRIPT_PROXY_URL", "").strip()
TRANSCRIPT_PROXY_HTTP_URL = os.getenv("TRANSCRIPT_PROXY_HTTP_URL", "").strip()
TRANSCRIPT_PROXY_HTTPS_URL = os.getenv("TRANSCRIPT_PROXY_HTTPS_URL", "").strip()
TRANSCRIPT_PROXY_HOST = os.getenv("TRANSCRIPT_PROXY_HOST", "").strip()
TRANSCRIPT_PROXY_PORT = os.getenv("TRANSCRIPT_PROXY_PORT", "").strip()
TRANSCRIPT_PROXY_USERNAME = os.getenv("TRANSCRIPT_PROXY_USERNAME", "").strip()
TRANSCRIPT_PROXY_PASSWORD = os.getenv("TRANSCRIPT_PROXY_PASSWORD", "").strip()

# ========================
# Data Models
# ========================

class TranscriptRequest(BaseModel):
    url: str

class TranscriptResponse(BaseModel):
    transcript: str
    video_id: str

class Excerpt(BaseModel):
    title: str = Field(description="The title of the insight")
    content: str = Field(description="The actual insight content of at least 1 page")

class ExcerptList(BaseModel):
    insights: List[Excerpt] = Field(description="List of insights")

class GenerateRequest(BaseModel):
    transcript: str

class DownloadRequest(BaseModel):
    title: str
    content: str
    format: str = "pdf"  # pdf or image

class DownloadResponse(BaseModel):
    data: str  # base64 encoded
    filename: str
    content_type: str

# ========================
# Helper Functions
# ========================

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r"(?<=v=)[^&#?]+",
        r"(?<=be/)[^&#?]+",
        r"(?<=embed/)[^&#?]+",
        r"(?<=shorts/)[^&#?]+"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(0)
    return None

def _parse_vtt_or_srt(content: str) -> str:
    """Parse VTT/SRT subtitle text into plain transcript."""
    cleaned_lines = []
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("WEBVTT"):
            continue
        if "-->" in stripped:
            continue
        if re.match(r"^\d+$", stripped):
            continue
        cleaned_lines.append(stripped)
    return " ".join(cleaned_lines)

def _parse_json3_captions(payload: str) -> str:
    """Parse YouTube json3 captions format into plain transcript."""
    data = json.loads(payload)
    chunks = []
    for event in data.get("events", []):
        for seg in event.get("segs", []):
            text = seg.get("utf8", "").strip()
            if text:
                chunks.append(text)
    return " ".join(chunks)

def _fetch_caption_url(url: str) -> str:
    """Fetch subtitle payload from a URL."""
    proxy_url = _compose_proxy_url()
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
    ) if proxy_url else urllib.request.build_opener()

    with opener.open(url, timeout=20) as response:
        return response.read().decode("utf-8", errors="ignore")

def _compose_proxy_url() -> str:
    """Build proxy URL from explicit vars first, then fallback to direct URL vars."""
    if TRANSCRIPT_PROXY_HOST and TRANSCRIPT_PROXY_PORT:
        if TRANSCRIPT_PROXY_USERNAME and TRANSCRIPT_PROXY_PASSWORD:
            username = quote(TRANSCRIPT_PROXY_USERNAME, safe="")
            password = quote(TRANSCRIPT_PROXY_PASSWORD, safe="")
            return f"http://{username}:{password}@{TRANSCRIPT_PROXY_HOST}:{TRANSCRIPT_PROXY_PORT}"
        return f"http://{TRANSCRIPT_PROXY_HOST}:{TRANSCRIPT_PROXY_PORT}"

    return TRANSCRIPT_PROXY_URL or TRANSCRIPT_PROXY_HTTPS_URL or TRANSCRIPT_PROXY_HTTP_URL

def _create_transcript_api_client() -> YouTubeTranscriptApi:
    """Create YouTubeTranscriptApi client with optional proxy config."""
    proxy_url = _compose_proxy_url()
    http_proxy = TRANSCRIPT_PROXY_HTTP_URL or proxy_url
    https_proxy = TRANSCRIPT_PROXY_HTTPS_URL or proxy_url

    if GenericProxyConfig and (http_proxy or https_proxy):
        return YouTubeTranscriptApi(
            proxy_config=GenericProxyConfig(
                http_url=http_proxy or "",
                https_url=https_proxy or ""
            )
        )
    return YouTubeTranscriptApi()

def _select_caption_track(info: dict) -> Optional[dict]:
    """Pick best available caption track with language and format priority."""
    preferred_langs = ["en", "en-US", "en-GB"]
    preferred_exts = ["json3", "srv3", "vtt", "ttml", "xml", "srt"]

    merged_tracks = {}
    for source in ("subtitles", "automatic_captions"):
        for lang, tracks in (info.get(source) or {}).items():
            merged_tracks.setdefault(lang, []).extend(tracks or [])

    if not merged_tracks:
        return None

    language_order = preferred_langs + [lang for lang in merged_tracks.keys() if lang not in preferred_langs]
    for lang in language_order:
        tracks = merged_tracks.get(lang, [])
        if not tracks:
            continue

        for ext in preferred_exts:
            for track in tracks:
                if track.get("ext") == ext and track.get("url"):
                    return track

        for track in tracks:
            if track.get("url"):
                return track

    return None

def fetch_transcript_with_ytdlp(video_id: str) -> Optional[str]:
    """Fallback transcript extraction via yt-dlp caption tracks."""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    proxy_url = _compose_proxy_url()
    if proxy_url:
        ydl_opts["proxy"] = proxy_url

    cookies_file = os.getenv("YTDLP_COOKIES_FILE")
    if cookies_file:
        ydl_opts["cookiefile"] = cookies_file

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)

    track = _select_caption_track(info or {})
    if not track:
        return None

    payload = _fetch_caption_url(track["url"])
    ext = (track.get("ext") or "").lower()

    if ext in {"json3", "srv3"}:
        transcript_text = _parse_json3_captions(payload)
    else:
        transcript_text = _parse_vtt_or_srt(payload)

    transcript_text = html.unescape(transcript_text).replace("\n", " ").strip()
    return transcript_text or None

def create_pdf_from_text(title: str, content: str) -> bytes:
    """Create a professionally styled PDF from text"""
    char_count = len(title) + len(content)
    estimated_font_size = math.sqrt(620000 / max(char_count, 1))
    font_size = min(max(estimated_font_size, 8), 36)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{ size: A4; margin: 2cm; }}
            body {{ 
                font-family: 'Segoe UI', Arial, sans-serif; 
                font-size: {font_size}px;
                color: #1a1a2e;
                line-height: 1.6;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                margin: -2cm -2cm 20px -2cm;
                text-align: center;
            }}
            h1 {{ 
                font-size: {font_size * 1.5}px;
                margin: 0;
                font-weight: 600;
            }}
            .content {{
                text-align: justify;
                color: #333;
            }}
            .footer {{
                position: fixed;
                bottom: 1cm;
                left: 0;
                right: 0;
                text-align: center;
                font-size: 10px;
                color: #888;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{title}</h1>
        </div>
        <div class="content">
            <p>{content}</p>
        </div>
        <div class="footer">
            Generated by Transcribai • YouTube Excerpt Generator
        </div>
    </body>
    </html>
    """

    buffer = BytesIO()
    pisa.CreatePDF(BytesIO(html.encode('utf-8')), buffer)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def pdf_to_image(pdf_content: bytes) -> bytes:
    """Convert PDF to PNG image"""
    pdf_document = fitz.open("pdf", pdf_content)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x scale for better quality
    image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    buffer = BytesIO()
    image.save(buffer, format="PNG", quality=95)
    return buffer.getvalue()

# ========================
# API Routes
# ========================

@app.get("/")
def root():
    return {
        "name": "Transcribai API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/api/transcript",
            "/api/generate",
            "/api/download"
        ]
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.post("/api/transcript", response_model=TranscriptResponse)
def get_transcript(request: TranscriptRequest):
    """Fetch transcript from YouTube video"""
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL. Please check the URL format.")
    
    try:
        api = _create_transcript_api_client()
        transcript = api.fetch(video_id)
        transcript_text = " ".join([entry.text for entry in transcript])
        return TranscriptResponse(transcript=transcript_text, video_id=video_id)
    except Exception as primary_error:
        try:
            fallback_text = fetch_transcript_with_ytdlp(video_id)
            if fallback_text:
                return TranscriptResponse(transcript=fallback_text, video_id=video_id)
        except Exception:
            pass

        error_msg = str(primary_error)
        normalized_error = error_msg.lower()

        if "disabled" in normalized_error:
            raise HTTPException(status_code=400, detail="Subtitles are disabled for this video.")
        if "unavailable" in normalized_error or "not found" in normalized_error:
            raise HTTPException(status_code=404, detail="Video not found or unavailable.")
        if "requestblocked" in normalized_error or "ipblocked" in normalized_error or "youtube is blocking requests" in normalized_error:
            proxy_hint = (
                " Set TRANSCRIPT_PROXY_URL (or TRANSCRIPT_PROXY_HTTP_URL + TRANSCRIPT_PROXY_HTTPS_URL) in Render."
                if not (TRANSCRIPT_PROXY_URL or TRANSCRIPT_PROXY_HTTP_URL or TRANSCRIPT_PROXY_HTTPS_URL)
                else " Current proxy configuration is set, but YouTube still blocked this route."
            )
            raise HTTPException(
                status_code=503,
                detail=(
                    "Transcript provider blocked your server IP (common on cloud hosts). "
                    "This request failed on both primary and fallback methods. "
                    "Use a proxy-enabled transcript service or residential proxy for production."
                    + proxy_hint
                )
            )

        if (
            "407" in normalized_error
            or "proxy authentication required" in normalized_error
            or "unable to connect to proxy" in normalized_error
            or "tunnel connection failed" in normalized_error
        ):
            raise HTTPException(
                status_code=502,
                detail=(
                    "Proxy authentication failed (407). Verify Oxylabs credentials and endpoint. "
                    "Recommended: set TRANSCRIPT_PROXY_HOST, TRANSCRIPT_PROXY_PORT, "
                    "TRANSCRIPT_PROXY_USERNAME, TRANSCRIPT_PROXY_PASSWORD in Render backend env."
                )
            )

        raise HTTPException(status_code=500, detail=f"Error fetching transcript: {error_msg}")

@app.post("/api/generate", response_model=ExcerptList)
def generate_excerpts(request: GenerateRequest):
    """Generate insights from transcript using AI"""
    if not request.transcript or len(request.transcript.strip()) < 100:
        raise HTTPException(status_code=400, detail="Transcript is too short to generate insights.")
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Server configuration error: GROQ_API_KEY is not set.")
    
    try:
        llm = ChatGroq(
            max_tokens=4096, 
            model="llama-3.3-70b-versatile", 
            api_key=GROQ_API_KEY,
            temperature=0.7
        )
        parser = PydanticOutputParser(pydantic_object=ExcerptList)
        
        prompt_template = PromptTemplate(
            template="""You are an expert content curator. Extract 3-4 key insights from the following YouTube transcript.

For each insight:
1. Create a compelling, descriptive title
2. Extract the exact content verbatim (at least 200-300 words each)
3. Focus on the most valuable, insightful, or interesting parts

Transcript:
{transcript}

{format_instructions}""",
            input_variables=["transcript"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        _input = prompt_template.format_prompt(transcript=request.transcript[:15000])  # Limit input
        output = llm.invoke(_input.to_string())
        
        return parser.parse(output.content)
        
    except Exception as e:
        print(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

@app.post("/api/download", response_model=DownloadResponse)
def download_excerpt(request: DownloadRequest):
    """Generate downloadable PDF or Image from insight"""
    try:
        pdf_bytes = create_pdf_from_text(request.title, request.content)
        
        if request.format == "image":
            image_bytes = pdf_to_image(pdf_bytes)
            return DownloadResponse(
                data=base64.b64encode(image_bytes).decode(),
                filename=f"{request.title[:30].replace(' ', '_')}.png",
                content_type="image/png"
            )
        else:
            return DownloadResponse(
                data=base64.b64encode(pdf_bytes).decode(),
                filename=f"{request.title[:30].replace(' ', '_')}.pdf",
                content_type="application/pdf"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating file: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
