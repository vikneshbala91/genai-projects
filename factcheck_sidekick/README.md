# Fact-Check Sidekick

A Flask-based web application for fact-checking claims using AI and web search capabilities. Built for Singapore newsrooms to verify claims and statements with credible sources.

## Features

- Interactive chatbot interface
- AI-powered fact-checking using Azure OpenAI
- Web search integration for source verification
- Session-based chat history
- Clean and responsive UI

## Setup

1. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # or
   venv\Scripts\activate  # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   Create a `.env` file in the project root with your Azure OpenAI credentials:
   ```
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   AZURE_OPENAI_API_VERSION=2024-12-01-preview
   AZURE_OPENAI_CHAT_DEPLOYMENT=your-deployment-name
   ```

   **Important:** Make sure your deployment name exists in your Azure OpenAI resource!

## Usage

### Web Application (Recommended)

1. Run the Flask app:
   ```bash
   cd src
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. Enter a claim or statement you want to fact-check

4. The AI will search for evidence and provide a verdict with sources

### Command Line

You can also run the original CLI version:
```bash
cd src
python azure_agent.py
```

## Dependencies

See [requirements.txt](requirements.txt) for a full list of dependencies.

## Development

To add new dependencies:
```bash
pip install package-name
pip freeze > requirements.txt
```
