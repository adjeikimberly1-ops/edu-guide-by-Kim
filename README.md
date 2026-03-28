# 🎓 EduGuide by Kim
> A personalized AI learning coach built with LangChain, Groq & Streamlit

##  Live Demo
 [Try EduGuide AI Live](https://edu-guide-by-kim-qm8t69jmbeceqcua6l33py.streamlit.app/)

## Features
- **Roadmap Builder** : personalised step-by-step learning plans.
- **Concept Explainer** : any topic in plain and simple language.
- **Resource Finder** : real free learning resources from the web.
- **Adaptive Quizzes** : MCQ, True/False & Short Answer, auto-difficulty
- **Progress Tracking** : streak, scores, topics & roadmaps saved to SQLite.
- **PDF Export** : download your full progress report.

##  Quick Start

### 1. Clone & install
```bash
git clone https://github.com/YOUR_USERNAME/eduguide-ai.git
cd eduguide-ai
pip install -r requirements.txt
```

### 2. Set up API keys
Create a `.env` file:
```
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```
Get your free keys at:
- Groq: https://console.groq.com
- Tavily: https://app.tavily.com

### 3. Run
```bash
streamlit run app.py
```

##  Deploy to Streamlit Community Cloud

1. Push this repo to GitHub (make sure `.env` and `*.db` are in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set main file to `app.py`
4. Go to **Settings → Secrets** and add:
```toml
GROQ_API_KEY = "your_groq_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```
5. Click **Deploy** - done! 

##  Project Structure
```
eduguide_ai/
├── app.py                        # Streamlit UI
├── requirements.txt              # Dependencies
├── .gitignore
├── .streamlit/
│   └── config.toml               # Theme & server config
└── agent/
    ├── __init__.py
    ├── core.py                   # ReAct agent setup
    ├── tools.py                  # 7 custom LangChain tools
    ├── database.py               # SQLite progress tracking
    └── pdf_export.py             # PDF report generation
```

##  Tech Stack
- **LangChain** : ReAct agent, tools & chains
- **Groq** : llama-3.3-70b-versatile LLM
- **Tavily** : real-time web search
- **SQLite** : local progress storage
- **fpdf2** : PDF report generation
- **Streamlit** : frontend UI