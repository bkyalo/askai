# Askia - Kenyan Knowledge Assistant

Askia is a Retrieval-Augmented Generation (RAG) chatbot designed to provide accurate, localized information to field workers in Kenya. It combines the power of large language models with a curated knowledge base of official Kenyan documents.

## Features

- 🌍 Multilingual support (English, Swahili, Sheng)
- 📚 Localized knowledge base
- 🔍 Context-aware responses
- 📱 Telegram bot interface
- 🚀 Fast and efficient RAG architecture

## Prerequisites

- Python 3.8+
- Telegram account
- Google API key for Gemini Pro
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Askia
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with the following content:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   GOOGLE_API_KEY=your_google_gemini_api_key
   ```

5. **Add your documents**
   Create a `documents` folder and add your PDF files:
   ```
   mkdir documents
   # Copy your PDF files here
   ```

6. **Load documents into the knowledge base**
   Run the document loader:
   ```bash
   python -c "from document_loader import DocumentLoader; loader = DocumentLoader(); docs = loader.load_directory('documents'); print(f'Loaded {len(docs)} chunks')"
   ```

## Running the Bot

1. **Start the Telegram bot**
   ```bash
   python app.py
   ```

2. **Interact with the bot**
   - Open Telegram and search for your bot
   - Send `/start` to begin
   - Ask questions about health, agriculture, or other topics

## Project Structure

- `app.py` - Main application with Telegram bot handlers
- `config.py` - Configuration settings
- `database.py` - Vector database operations
- `document_loader.py` - Document processing and loading
- `requirements.txt` - Python dependencies

## Adding More Documents

1. Place new PDFs in the `documents` folder
2. The bot will automatically process them when restarted

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Google Gemini API for the language model
- ChromaDB for vector storage
- Python-Telegram-Bot for the Telegram interface
