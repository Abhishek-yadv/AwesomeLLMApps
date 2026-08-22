# Transcribai - AI-Powered Social Media Insights 🚀

**Transcribai** is a powerful SaaS tool that transforms lengthy videos from YouTube, Instagram, LinkedIn, and TikTok into concise, actionable insights using AI.

![Transcribai Demo](https://via.placeholder.com/800x400?text=Transcribai+Interface+Preview)

## ✨ Features

- **Multi-Platform Support**: Fetch transcripts from YouTube, Instagram, LinkedIn, and TikTok.
- **AI-Powered Insights**: Uses Groq (Llama 3 70B) to extract key takeaways and summaries.
- **Premium UI**: Stunning dark-mode interface built with Next.js, Framer Motion, and Tailwind CSS.
- **One-Click Downloads**: Export insights as professionally styled PDFs or shareable Images.
- **Dynamic Adaptation**: The interface adapts its colors and icons based on the selected platform.

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** (App Router)
- **TypeScript**
- **Tailwind CSS v4** + **Framer Motion**
- **Lucide React** (Icons)

### Backend
- **FastAPI** (Python)
- **LangChain + Groq** (AI Logic)
- **YouTube Transcript API**
- **yt-dlp fallback** (caption extraction fallback for cloud-hosted environments)
- **xhtml2pdf** & **PyMuPDF** (PDF/Image Generation)

## 🚀 Getting Started

### Prerequisites
- Node.js & npm
- Python 3.9+
- Groq API Key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/USER/Transcribai.git
   cd Transcribai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   # Backend runs on http://localhost:8000
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   # Frontend runs on http://localhost:3000
   ```

4. **Environment Variables**
   - Create a `.env` in `backend/` and add:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
       # Recommended for production on Render (single proxy URL)
       TRANSCRIPT_PROXY_URL=http://username:password@proxy-host:port
       # Or provide separate values
       # TRANSCRIPT_PROXY_HTTP_URL=http://username:password@proxy-host:port
       # TRANSCRIPT_PROXY_HTTPS_URL=http://username:password@proxy-host:port
       # Optional: absolute path to cookies file for yt-dlp fallback (if needed)
       YTDLP_COOKIES_FILE=/path/to/cookies.txt
     ```

## ☁️ Render / Cloud Note

Some cloud IP ranges are blocked by YouTube for transcript scraping. The backend now tries:
1. `youtube_transcript_api` (primary)
2. `yt-dlp` captions fallback (automatic/manual subtitle tracks)

If both fail due to network/IP blocking, use a proxy-enabled setup in production.

## 🚀 Render Deployment (Verified Settings)

Configure two Render web services (backend + frontend) with these values:

### 1) Backend service (Python)
- **Root Directory:** `backend`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Required Environment Variables:**
   - `GROQ_API_KEY=your_groq_api_key`
- **Recommended Environment Variables (to bypass cloud IP blocks):**
   - `TRANSCRIPT_PROXY_URL=http://username:password@proxy-host:port`
   - or both `TRANSCRIPT_PROXY_HTTP_URL=...` and `TRANSCRIPT_PROXY_HTTPS_URL=...`
   - or (recommended to avoid encoding/auth issues):
     - `TRANSCRIPT_PROXY_HOST=pr.oxylabs.io`
     - `TRANSCRIPT_PROXY_PORT=7777`
     - `TRANSCRIPT_PROXY_USERNAME=<proxy_username>`
     - `TRANSCRIPT_PROXY_PASSWORD=<proxy_password>`
- **Optional Environment Variables:**
   - `YTDLP_COOKIES_FILE=/opt/render/project/src/backend/cookies.txt`

### 2) Frontend service (Next.js)
- **Root Directory:** `frontend`
- **Build Command:** `npm ci && npm run build`
- **Start Command:** `npm run start -- -p $PORT`
- **Required Environment Variables:**
   - `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-service>.onrender.com/api`

### Why this matters
- Frontend now reads API URL from `NEXT_PUBLIC_API_BASE_URL` instead of hardcoded localhost.
- Backend uses `GROQ_API_KEY` from environment.
- Uvicorn binds correctly to Render's dynamic port via `$PORT`.

## 📝 API Endpoints

- `POST /api/transcript` - Fetch transcript from URL
- `POST /api/generate` - Generate insights from transcript
- `POST /api/download` - Download insight as PDF/Image

## 🤝 Contributing

Contributions are welcome! Please fork the repo and submit a PR.

## 📄 License

MIT License © 2026 Transcribai
