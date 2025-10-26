# Askia - Kenyan Knowledge Assistant

Askia is a Retrieval-Augmented Generation (RAG) chatbot designed to provide accurate, localized information to field workers in Kenya. It combines the power of large language models with a curated knowledge base of official Kenyan documents.

## Features

- 🌍 Multilingual support (English, Swahili, Sheng)
- 📚 Localized knowledge base
- 🔍 Context-aware responses
- 📱 Telegram bot interface
- 🚀 Fast and efficient RAG architecture
- ⚡ Easy document ingestion with `setup_database.sh`

## Prerequisites

- Python 3.8+
- Telegram account
- OpenAI API key
- Telegram Bot Token from [@BotFather](https://t.me/botfather)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/bkyalo/askai.git
   cd askai
   ```

2. **Set up the environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file with your API key:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```
   Your `.env` file should look like this:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Add your documents**
   ```bash
   mkdir -p documents
   # Copy your PDF files to the documents/ directory
   ```

5. **Initialize the database**
   ```bash
   chmod +x setup_database.sh
   ./setup_database.sh
   ```

6. **Start the bot**
   ```bash
   python app.py
   ```

## Updating Documents

To update the knowledge base with new documents:

1. Add new PDF files to the `documents/` directory
2. Run the setup script again:
   ```bash
   ./setup_database.sh
   ```
   This will rebuild the entire vector database with all documents.

## Project Structure

```
.
├── app.py              # Main application entry point
├── config.py           # Configuration settings
├── database.py         # Vector database operations
├── document_loader.py  # Document processing utilities
├── requirements.txt    # Python dependencies
└── documents/          # Directory for knowledge base documents
    └── *.pdf           # PDF documents for the knowledge base
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Your Telegram bot token from @BotFather | ✅ |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |
| `CHROMA_DB_PATH` | Path to store the vector database (default: `chroma_db/`) | ❌ |

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
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
