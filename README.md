---
title: career_ai
app_file: app.py
sdk: gradio
sdk_version: 6.3.0
---
# Career AI

A quick example of AI-powered chat assistant that represents a candidate's professional profile. Built with Gradio and OpenAI's latest release of [openai-python](https://github.com/openai/openai-python) v2.15 using [Responses API](https://platform.openai.com/docs/api-reference/responses), this application provides an interactive interface for answering questions about career background, skills, experience, and projects based on LinkedIn profile data.

## Features

- 🤖 **AI-Powered Chat Interface**: Interactive conversational interface powered by OpenAI's generative AI models
- 📄 **PDF Profile Integration**: Automatically extracts and processes LinkedIn profile and projects from PDF files
- 🔧 **Function Calling**: Built-in tools for recording user contact details and tracking unanswered questions
- 📱 **Pushover Notifications**: Optional integration with Pushover for real-time notifications
- 🎨 **Modern UI**: Clean, responsive web interface built with Gradio
- 🔄 **Conversation Context**: Maintains conversation history for natural, contextual interactions
- ⚡ **Error Handling**: Robust error handling with graceful degradation

## Requirements

- Python 3.12 or higher
- OpenAI API key
- (Optional) Pushover account for notifications

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd career_ai
   ```

2. **Install dependencies**:
   
   Using `uv` (recommended):
   ```bash
   uv sync
   ```
   
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_TOKEN=your_pushover_token_here  # Optional
   PUSHOVER_USER=your_pushover_user_here    # Optional
   ```

4. **Prepare resource files**:
   
   Ensure the following files exist in the `resources/` directory:
   - `ProfileLinkedIn.pdf` - LinkedIn profile export
   - `ProjectsLinkedIn.pdf` - LinkedIn projects export
   - `summary.txt` - Professional summary text

5. **Configure candidate information**:
   
   Update `config.py` with your details:
   ```python
   CANDIDATE_NAME = "Your Name"
   GPT_RESPONDER_MODEL = "gpt-5-mini"
   ```

## Usage

Run the application:

```bash
uv run app.py
```

The Gradio interface will launch and display a local URL (typically `http://127.0.0.1:7860`). Open this URL in your web browser to start chatting with the AI assistant.

### How It Works

1. The application loads your professional information from PDF files and text summaries
2. Users interact with the AI assistant through the web interface
3. The AI answers questions about your career, skills, and experience
4. User contact details and unanswered questions are automatically recorded (if Pushover is configured)

## Project Structure

```
career_ai/
├── app.py                 # Main application file
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
├── README.md              # This file
└── resources/
    ├── ProfileLinkedIn.pdf
    ├── ProjectsLinkedIn.pdf
    └── summary.txt
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `PUSHOVER_TOKEN` | No | Pushover API token for notifications |
| `PUSHOVER_USER` | No | Pushover user key for notifications |

### Application Settings

Edit `config.py` to customize:
- Candidate name
- AI model selection
- System prompt behavior

## Technologies Used

- **Gradio** (6.3.0+) - Web interface framework
- **OpenAI** (2.15.0+) - AI model integration
- **pypdf** (6.6.0+) - PDF text extraction
- **requests** (2.32.5+) - HTTP client for notifications
- **python-dotenv** - Environment variable management

## Features in Detail

### Function Calling

The application includes two built-in functions:

1. **`record_user_details`**: Captures user contact information when they express interest
2. **`record_unknown_question`**: Logs questions the AI cannot answer for knowledge base improvement

### Error Handling

- Graceful handling of missing Pushover credentials
- PDF parsing error recovery
- API request timeout protection
- Maximum iteration limits to prevent infinite loops

## Development

### Code Quality

The codebase follows Python best practices:
- Type hints throughout
- Comprehensive docstrings
- Error handling and logging
- Modular design with separation of concerns

### Logging

Logging is configured at WARNING level by default. Adjust the log level in `app.py`:

```python
logging.basicConfig(level=logging.INFO)  # For more verbose logging
```

## Troubleshooting

### Common Issues

1. **Missing resource files**: Ensure all PDFs and `summary.txt` are in the `resources/` directory
2. **Missing config**: Ensure all necessary configurations are in place under the `config.py` 
3. **OpenAI API errors**: Verify your API key is set correctly in `.env`
4. **Pushover notifications not working**: Check that both `PUSHOVER_TOKEN` and `PUSHOVER_USER` are set, or remove them if notifications aren't needed

## License
MIT License

Copyright (c) 2026 Rahul Anand

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Contributing

Open for Contributions

## Contact

Contact me @ rahul168@outlook.com

---

Built with ❤️ using Python and Gradio
