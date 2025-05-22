# AI Text Generator

A powerful text editor application that combines traditional text editing capabilities with AI-powered features. Built with Python and Tkinter, this application allows users to generate, transform, and search text using Google's Gemini AI model.

## Features

- Text editing with line numbers
- AI-powered text generation using Google's Gemini model
- Web search integration
- Text transformation capabilities
- Dark theme interface
- File operations (New, Open, Save, Save As)

## Requirements

- Python 3.7 or higher
- Internet connection for AI features and web search

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Dapper-D/ai_text_gen.git
cd ai_text_gen
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. (Optional) Create a `.env` file in the project root and add your Gemini API key if you want to use your own:
```
GEMINI_API_KEY=your_api_key_here
```

Note: The application comes with a free-tier Gemini API key by default. You only need to create a `.env` file if you want to use your own API key. To get your own Gemini API key, visit https://makersuite.google.com/app/apikey.

## Usage

Run the application:
```bash
python text_editor.py
```

### Main Features

1. **Text Generation**
   - Enter your prompt in the AI Generation section
   - Click "Generate" to create AI-generated text using Gemini AI

2. **Web Search**
   - Enter your search query
   - Click "Search" to find relevant information
   - Use "Add to Document" to insert search results

3. **Text Transformation**
   - Select text in the main editor
   - Click "Copy Selected" to move it to the transformation area
   - Enter transformation instructions
   - Click "Apply Changes" to transform the text using Gemini AI

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 