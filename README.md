# 🌐 Agentic Browser Assistant

An AI agent that "browses" the web via tools to answer queries instantly, powered by Cerebras' ultra-fast inference API.

## 🚀 Features

- **🧠 Agentic AI**: AI autonomously selects and uses tools based on query analysis
- **⚡ Instant Responses**: Powered by Cerebras' Llama3.1-8B model at lightning speed
- **🔧 Smart Tool Selection**: AI chooses between web search, URL scraping, or combined approaches
- **🌐 Web Search**: Free web search using DuckDuckGo (no API keys required)
- **📄 Web Scraping**: Robust BeautifulSoup-powered content extraction with error handling
- **🎯 Context-Aware**: Combines multiple information sources with AI reasoning
- **💻 CLI Interface**: Easy-to-use command-line interface with real-time progress

## 📦 Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. API Configuration
Create a `.env` file with your Cerebras API key:
```
CEREBRAS_API_KEY=your_api_key_here
```

Get your free API key at: https://cloud.cerebras.ai

### 3. Test Setup
```bash
python test_setup.py
```

## 🎯 Usage

### Interactive Mode
```bash
python main.py
```

### Demo Mode (Recommended for first-time users)
```bash
python demo_agentic.py
```

### Test the Enhanced System
```bash
python test_agentic_tools.py
```

### Example Queries
The AI will automatically select the best tools for each query:
- **Research**: "Find the best laptop under $1000"
- **News**: "What are the latest AI developments?"
- **Comparison**: "Compare Python vs JavaScript for web development"
- **Direct URL**: "Scrape information from https://example.com"
- **Current Events**: "What is the current Bitcoin price?"

### Programmatic Usage
```python
from main import AgenticBrowserAssistant

assistant = AgenticBrowserAssistant()
response = assistant.process_query("Your question here")
print(response)
```

### Direct Cerebras Client
```python
from cerebras_client import get_completion

response = get_completion("Hello, world!")
print(response)
```

## 🏗️ Agentic Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │ -> │  AI Tool Selector│ -> │   Tool Router   │
│                 │    │   (Cerebras)     │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                ↓                        ↓
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Final Response  │ <- │  AI Synthesizer  │ <- │ Tool Execution  │
│   (Cerebras)    │    │   (Cerebras)     │    │ • web_search    │
└─────────────────┘    └──────────────────┘    │ • scrape_url    │
                                                │ • search_scrape │
                                                └─────────────────┘
```

### Agentic Flow:
1. **Query Analysis**: AI analyzes user intent
2. **Tool Selection**: AI chooses optimal tool(s) 
3. **Tool Execution**: Selected tools gather information
4. **Response Synthesis**: AI creates comprehensive answer

## 📁 Project Structure

```
AIWebWarden/
├── venv/                    # Virtual environment
├── .env                     # API keys (not in git)
├── .gitignore              # Git ignore file
├── requirements.txt        # Dependencies
├── cerebras_client.py      # Cerebras API client
├── tools.py               # Agentic web tools
├── main.py                # Main assistant with agentic logic
├── test_setup.py          # Basic setup verification
├── test_agentic_tools.py  # Enhanced agentic system tests
├── demo_agentic.py        # Interactive demo showcase
└── README.md              # This file
```

## 🔧 Configuration

### Models Available
- `llama3.1-8b` (default) - Fast and efficient
- `llama3.1-70b` - More capable but slower
- Check Cerebras docs for latest models

### Customization
Edit `cerebras_client.py` to change:
- Model selection
- Temperature settings
- Max tokens
- Other parameters

## 🧪 Testing

Run the test suite:
```bash
python test_setup.py
```

This verifies:
- ✅ Cerebras API connection
- ✅ Assistant initialization  
- ✅ Web search functionality

## 🎬 Demo Features

Perfect for video demonstrations:
1. **Real-time Processing**: Watch the agent search and respond instantly
2. **Step-by-Step Visibility**: See search → process → respond flow
3. **Diverse Queries**: Test with shopping, research, coding questions
4. **Speed Showcase**: Emphasize Cerebras' instant inference speed

## 🔄 Next Steps

### Phase 2 Enhancements:
- [ ] Add ReAct (Reasoning + Acting) pattern with LangChain
- [ ] Implement tool selection logic
- [ ] Add more specialized tools (price comparison, code search)
- [ ] Web UI with Streamlit/Flask
- [ ] Conversation memory
- [ ] Source citation improvements

### Advanced Features:
- [ ] Multi-step reasoning chains
- [ ] Custom tool creation
- [ ] Integration with more APIs
- [ ] Caching for repeated queries
- [ ] Async processing for multiple queries

## 📊 Performance

- **Search Speed**: ~1-2 seconds
- **AI Processing**: ~0.5-1 seconds (Cerebras advantage!)
- **Total Response Time**: ~2-4 seconds
- **Cost**: Minimal with Cerebras free tier

## 🛠️ Troubleshooting

### Common Issues:
1. **API Key Error**: Check `.env` file exists and has correct key
2. **Import Errors**: Ensure virtual environment is activated
3. **Search Failures**: Check internet connection
4. **Model Not Found**: Update model name in `cerebras_client.py`

### Debug Mode:
Add print statements in `main.py` to trace execution flow.

## 📝 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Built with ❤️ using Cerebras AI, DuckDuckGo Search, and Python**