## 🗞️ AIJournalistAgent

AIJournalistAgent is a Streamlit app that uses OpenAI GPT-4 to help create high-quality articles on any topic. It streamlines the process of researching, writing, and editing, making content creation faster and easier.

### ✨ Features

- 🔍 Searches the web for relevant information on your chosen topic
- ✍️ Writes well-structured and engaging articles
- 🖋️ Edits and refines content to meet high journalistic standards

### 🚀 Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/Abhishek-yadv/AwesomeLLMApps/tree/main/AIJournalistAgent
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get your OpenAI API Key:
   - 🔑 Sign up for an [OpenAI account](https://platform.openai.com/) and obtain your API key

4. Get your SerpAPI Key:
   - 🔑 Sign up for a [SerpAPI account](https://serpapi.com/) and get your API key

5. Run the app:
   ```bash
   streamlit run main.py
   ```

### 🧠 How It Works

AIJournalistAgent uses three main components:

1. 🕵️ Searcher:
   - Generates search terms based on the given topic
   - Searches the web for relevant URLs using SerpAPI

2. 📝 Writer:
   - Retrieves text from the provided URLs using NewspaperToolkit
   - Writes an article based on the extracted information

3. ✨ Editor:
   - Coordinates the workflow between the Searcher and Writer
   - Performs final editing and refinement of the article

Try AIJournalistAgent today and experience a new way to create content quickly and efficiently! 🚀📰
