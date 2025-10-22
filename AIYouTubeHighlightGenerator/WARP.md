# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AIYouTubeHighlightGenerator is a Streamlit web application that uses AI to automatically generate engaging excerpts from YouTube video transcripts. It extracts transcripts from YouTube videos, processes them through Groq's LLM (llama3-70b-8192 model), and generates 3-4 structured excerpts with downloadable PDFs and images.

## Development Commands

### Setup
```powershell
# Create virtual environment
python -m venv env

# Activate environment (Windows PowerShell)
.\env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set Groq API key (required)
$env:GROQ_API_KEY = "your_api_key_here"
```

### Running the Application
```powershell
# Start the Streamlit app
streamlit run main.py
```

### Dependency Management
```powershell
# Generate requirements.txt after adding packages
pip freeze > requirements.txt
```

## Architecture

### Application Flow
1. **URL Parsing** → `extract_video_id()` extracts video ID using regex patterns for standard and shortened YouTube URLs
2. **Transcript Fetching** → `get_transcript()` uses YouTubeTranscriptApi to retrieve video transcript text
3. **AI Processing** → `generate_excerpts()` sends transcript to Groq LLM with structured output parsing via Pydantic models
4. **PDF Generation** → `create_pdf_from_text()` converts excerpts to PDFs using xhtml2pdf with dynamic font sizing
5. **Image Conversion** → `pdf_to_image()` renders PDF pages to PNG using PyMuPDF (fitz)

### Key Components

**Pydantic Models (lines 17-22)**
- `Excerpt`: Defines structure for each excerpt (title + content)
- `ExcerptList`: Wraps list of excerpts for LLM output parsing
- Used with `PydanticOutputParser` to ensure structured AI responses

**LLM Configuration (line 41)**
- Model: `llama3-70b-8192`
- Max tokens: 4096
- API: Groq via langchain_groq
- Prompt requires 300+ word excerpts to ensure full-page content

**PDF Generation (lines 68-107)**
- Dynamic font sizing based on character count to fill A4 pages
- Font size constrained between 8-36px
- HTML-to-PDF conversion with embedded CSS styling
- A4 page format with 1cm margins

**State Management**
- API key checked via environment variable first, fallback to Streamlit input
- Transcript displayed in text area before excerpt generation
- Excerpts displayed in 2-column grid layout using `st.columns(2)`

### Dependencies

Core libraries:
- **streamlit**: Web UI framework
- **youtube_transcript_api** (v1.2.3+): Transcript extraction - uses `.fetch()` method instead of deprecated `.get_transcript()`
- **langchain_groq**: LLM integration with structured output
- **pydantic**: Data validation and parsing
- **xhtml2pdf**: HTML-to-PDF conversion
- **PyMuPDF (fitz)**: PDF manipulation and rendering
- **Pillow**: Image processing

**Important**: The youtube-transcript-api had a breaking change from v0.6.x to v1.2.x. The old `.get_transcript()` method is no longer available. Use `YouTubeTranscriptApi().fetch(video_id)` instead, which returns objects with `.text` attributes rather than dictionaries.

## Important Patterns

### Error Handling
- Transcript fetching wrapped in try-except with user-friendly error messages
- Invalid URL validation before transcript fetch
- API key validation with app stop if missing

### Regex Patterns for YouTube URLs
Supports two formats:
- Standard: `https://www.youtube.com/watch?v=VIDEO_ID`
- Shortened: `https://youtu.be/VIDEO_ID`

### Content Generation
- LLM prompt specifically requests 3-4 excerpts
- Each excerpt must be "at least a page long (300 words)"
- Output parsed through Pydantic ensures consistent structure

### Base64 Encoding
Download links use base64-encoded content embedded in HTML `<a>` tags with data URIs for both PDF and PNG downloads.

## Environment Variables

- `GROQ_API_KEY`: Required for LLM access. Can be set via environment or entered in the Streamlit UI.

## Live Demo

Deployed at: https://aiyoutubehighlightgenerator-isfzha3fw6s6dwpieztp5o.streamlit.app
