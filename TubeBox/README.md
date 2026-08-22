# YouTube to Ebook

Transform YouTube videos from your favorite channels into beautifully formatted EPUB ebooks.

## Features

- Fetches latest videos from YouTube channels (automatically filters out Shorts)
- Extracts transcripts from videos
- Uses Claude AI to transform transcripts into polished magazine-style articles
- Generates EPUB ebooks readable on any device
- Optional: Email delivery with ebook attachment
- Optional: Web dashboard for easy management

## Quick Start

1. **Clone and install:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/youtube-to-ebook.git
   cd youtube-to-ebook
   pip install -r requirements.txt
   ```

2. **Set up API keys:**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

3. **Add your channels:**
   ```bash
   # Edit channels.txt with YouTube channel handles
   @mkbhd
   @veritasium
   @3blue1brown
   ```

4. **Generate your ebook:**
   ```bash
   python main.py
   ```

## Getting API Keys

### YouTube Data API (Free)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "YouTube Data API v3"
4. Create credentials → API Key
5. Copy to `.env`

### Anthropic API
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Create an API key
3. Copy to `.env`

## Web Dashboard

Launch a friendly web interface:
```bash
pip install streamlit
python -m streamlit run dashboard.py
```

## Automation (Mac)

Run automatically every week:
```bash
# Copy the plist to LaunchAgents
cp com.youtube.newsletter.plist ~/Library/LaunchAgents/

# Load it
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.youtube.newsletter.plist
```

## Troubleshooting

### "ModuleNotFoundError" when running automation

Your Mac may have multiple Python installations. The automation scripts use `python3`, but your packages might be installed in a different Python.

**Fix:** Find your Python path and update the scripts:
```bash
# Find where your Python is
which python3

# Update run_newsletter.sh and dashboard.py with the full path
# Example: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3
```

## Known Issues & Solutions

This project documents several YouTube API quirks:

| Problem | Solution |
|---------|----------|
| Shorts not filtered by duration | Check `/shorts/` URL pattern |
| Search API not chronological | Use uploads playlist instead |
| Transcript API syntax changed | Use instance method `ytt_api.fetch()` |
| Cloud servers blocked | Run locally, not GitHub Actions |
| Names misspelled in transcripts | Include video description in Claude context |
| Articles truncated mid-sentence | Increase `max_tokens` in write_articles.py |

See [SKILL.md](SKILL.md) for detailed explanations.

## Project Structure

```
├── main.py              # Run the full pipeline
├── get_videos.py        # Fetch videos from YouTube
├── get_transcripts.py   # Extract video transcripts
├── write_articles.py    # Transform to articles with Claude
├── send_email.py        # Create EPUB & send email
├── dashboard.py         # Streamlit web dashboard
├── video_tracker.py     # Track processed videos
├── channels.txt         # Your channel list
├── .env                 # Your API keys (not committed)
└── newsletters/         # Archive of generated ebooks
```

## License

MIT - Use freely, modify as needed.

---

Built with Claude AI
