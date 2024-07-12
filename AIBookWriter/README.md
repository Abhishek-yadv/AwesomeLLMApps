# 📚✨ AIBookWriter

Transform ideas into full-length books with AI magic! 🚀🤖

## 📝 Description

AIBookWriter is a cutting-edge Streamlit web application that harnesses the power of AI to automatically craft entire books from simple prompts. It's the perfect tool for authors, content creators, researchers, and anyone looking to quickly generate comprehensive, structured content! 📖💡🔍

## 🌟 Features

- 💡 AI-powered book title generation
- 📚 Comprehensive book structure creation
- 🧠 AI-driven content generation using Groq's LLM
- 📊 Sleek, user-friendly interface for displaying book sections
- 📥 One-click PDF and text downloads
- 👁️ Real-time preview of generated content
- 📈 Detailed generation statistics
- 🎨 Beautifully formatted output

## 🛠️ Tech Stack

- 🖥️ Streamlit: Powering our intuitive web interface
- 🤖 Groq: Unleashing AI-powered text generation
- 📄 WeasyPrint: Crafting PDFs with finesse
- 🖋️ Markdown: Formatting text beautifully
- 🔐 python-dotenv: Managing environment variables securely

## 🚀 Getting Started

1. Clone the magical repository:
   ```sh
   git clone https://github.com/YourUsername/AIBookWriter
   cd AIBookWriter
   ```

2. Create your virtual environment (your writing sanctuary):
   ```sh
   python3 -m venv env
   source env/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the enchanted packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Summon your Groq API key:
   - Create a `.env` file in the project root and add:
     ```
     GROQ_API_KEY=your_groq_api_key
     ```
   - Alternatively, the app will ask for it when you start your journey.

## 🧙‍♂️ Casting the Spell (Usage)

To bring the application to life, chant:

```sh
streamlit run app.py
```

Follow these magical steps:
1. 🔑 Enter your Groq API key if prompted.
2. 📝 Enter your book topic in the mystical input field.
3. ✨ (Optional) Provide additional instructions for content generation.
4. 🚀 Click "Generate" to unleash the AI.
5. 🎉 Behold as your book materializes section by section, and download it as a scroll (PDF) or manuscript (text file) when complete.

## 🧠 The Sorcery Behind the Scenes

1. 🎭 The app first conjures an enticing title for your book using AI.
2. 📜 It then summons a comprehensive book structure.
3. 🤖 For each section, the AI channels its creativity to generate detailed content.
4. 📊 Real-time statistics keep you informed of the magical process.
5. 📚 The completed book appears before your eyes, ready to be shared with the world.

## 🧙‍♀️ Arcane Functions

### 🔮 generate_book_title(prompt)
Divines an captivating title for your book.

### 📜 generate_book_structure(prompt)
Conjures a detailed structure for your tome.

### 🧪 generate_section(prompt, additional_instructions)
Channels the Groq language model to transmute prompts into rich content for each section.

### 📄 create_pdf_file(content)
Manifests a PDF scroll from the generated book content.

### 🖼️ create_markdown_file(content)
Transforms the book into a beautifully formatted markdown manuscript.

## 🤝 Join the Writers' Coven (Contributing)

Your contributions are welcome! Feel free to cast a Pull Request and join our magical community of AI-assisted authors.

## 📜 Scroll of Rights (License)

This project is protected by the MIT License spell. Consult the `LICENSE` scroll for the full incantation.

## 🙏 Gratitude to the Elders

- 🧙‍♂️ Streamlit sages for their framework of wonders
- 🧠 Groq archmages for their powerful language model
- 🌟 All the open-source wizards whose libraries made this project possible

---

Crafted with ❤️ and a sprinkle of ✨ by Abhishek Yadav

May your books be ever insightful! 📚💫
