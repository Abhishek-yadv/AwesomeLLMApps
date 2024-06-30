# 🎥✨ AIYouTubeHighlightGenerator

Transform YouTube content into captivating excerpts with AI magic! 🚀🤖

## 📝 Description

AIYouTubeHighlightGenerator is a cutting-edge Streamlit web application that harnesses the power of AI to automatically craft engaging excerpts from YouTube video transcripts. It's the perfect tool for content creators, marketers, researchers, and anyone looking to quickly distill the essence of lengthy videos! 🎬💡🔍

## 🌟 Features

- 🔗 Smart YouTube URL parsing
- 📜 Lightning-fast transcript fetching
- 🧠 AI-powered excerpt generation using Groq's LLM
- 📊 Sleek, user-friendly interface for displaying excerpts
- 📥 One-click PDF and image downloads
- 👁️ Instant preview of generated excerpts
- 🎨 Beautifully formatted output

## 🛠️ Tech Stack

- 🖥️ Streamlit: Powering our intuitive web interface
- 🎞️ youtube_transcript_api: Fetching video transcripts with ease
- 🤖 langchain_groq: Unleashing AI-powered text generation
- 📄 PyMuPDF (fitz): Handling PDFs like a pro
- 🖼️ Pillow (PIL): Image processing wizardry
- 🏗️ xhtml2pdf: Crafting PDFs from HTML with finesse

## 🚀 Getting Started

1. Clone the magic repository:
   ```sh
   git clone https://github.com/Abhishek-yadv/AwesomeLLMApps/tree/main/AIYouTubeHighlightGenerator
   cd AIYouTubeHighlightGenerator
   ```

2. Create your virtual environment (your coding sanctuary):
   ```sh
   python3 -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the enchanted packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Summon your Groq API key:
   - Option 1: Whisper it to your environment:
     ```sh
     export GROQ_API_KEY=your_groq_api_key
     ```
   - Option 2: The app will ask for it when you start your journey.

## 🧙‍♂️ Casting the Spell (Usage)

To bring the application to life, chant:

```sh
streamlit run app.py
```

Follow these magical steps:
1. 🔑 Enter your Groq API key if the app asks for it.
2. 🔗 Paste a YouTube video URL into the mystical input field.
3. 🚀 Click "Generate Excerpts" to unleash the AI.
4. 🎉 Behold the generated excerpts, download them as scrolls (PDFs) or paintings (images), and preview them in the enchanted app.

## 🌈 Experience the Magic Live

Visit our live demo and witness the power of AIYouTubeHighlightGenerator:
[🔮 AIYouTubeHighlightGenerator Live](https://aiyoutubehighlightgenerator-isfzha3fw6s6dwpieztp5o.streamlit.app)

## 🧠 The Sorcery Behind the Scenes

1. 🔍 Our app extracts the secret video ID from the YouTube URL.
2. 📜 It summons the video transcript using ancient YouTube magic.
3. 🤖 The transcript is then whispered to the Groq language model, which divines structured excerpts.
4. 🖼️ These excerpts materialize in the Streamlit interface, ready to be captured as PDFs or images.
5. 📄 PDFs are conjured using xhtml2pdf and transformed into visual previews with PyMuPDF sorcery.

## 🧙‍♀️ Arcane Functions

### 🔮 extract_video_id(url)
Deciphers the video ID from a YouTube URL incantation.

### 📜 get_transcript(video_id)
Summons the transcript for a given YouTube video ID.

### 🧪 generate_excerpts(transcript)
Channels the Groq language model to transmute the transcript into structured excerpts.

### 📄 create_pdf_from_text(title, content)
Manifests a PDF scroll from the excerpt title and content.

### 🖼️ pdf_to_image(pdf_content)
Transfigures the first page of a PDF into a visual image for previewing.

## 🤝 Join the Coven (Contributing)

Your contributions are welcome! Feel free to cast a Pull Request and join our magical community.

## 📜 Scroll of Rights (License)

This project is protected by the MIT License spell. Consult the `LICENSE` scroll for the full incantation.

## 🙏 Gratitude to the Elders

- 🧙‍♂️ Streamlit sages for their framework of wonders
- 🧠 Groq archmages for their powerful language model
- 🌟 All the open-source wizards whose libraries made this project possible

---

Crafted with ❤️ and a sprinkle of ✨ by Abhishek Yadav

May your excerpts be ever insightful! 📼💫
