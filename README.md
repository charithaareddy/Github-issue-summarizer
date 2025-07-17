# 🧠 GitHub Issue Summarizer

A full-stack Python app that fetches a GitHub issue (title, body, comments), summarizes the content using Hugging Face's BART model, classifies the issue type (bug, feature, documentation, etc.), assigns a priority score, and suggests relevant labels — all through an easy-to-use Streamlit interface.

---

## 🔧 Features

- 🐙 Fetch GitHub issues by URL and number  
- 🧠 Summarize issues using **Hugging Face's BART** model  
- 🎯 Classify issue type and assign **priority scores**  
- 🏷️ Suggest useful **GitHub labels**  
- ⚡ Built with **FastAPI** (backend) and **Streamlit** (frontend)  
- 📦 Works locally with **Hugging Face API** or can be extended to offline models  

---

## 🛠️ Tech Stack

- Python 3.8+
- FastAPI
- Streamlit
- Hugging Face Transformers API (`facebook/bart-large-cnn`)
- Pydantic, Requests

---

## 📁 Project Structure

github-issue-summarizer/
│
├── main.py # FastAPI backend
├── app.py # Streamlit frontend
├── frontend.py # GitHub issue fetcher utility
├── requirements.txt # Dependencies
└── README.md

1.Install required packages

2.. Add Hugging Face API Token
Go to 👉 https://huggingface.co/settings/tokens
Click "New Token" and copy it

3.Set it in your PowerShell terminal before starting the app:
$env:HF_TOKEN="your_token_here"
✅ You do not need a .env file if you're doing this manually in the terminal.

4.🖥️ Run the App
Start Backend (FastAPI)
uvicorn main:app --reload
Backend runs at: http://127.0.0.1:8000

Start Frontend (Streamlit)
Open a new PowerShell window (or tab) and run:
streamlit run app.py
Frontend runs at: http://localhost:8501
5.Sample API Usage
POST /analyze_issue
json
{
  "repo_url": "https://github.com/facebook/react",
  "issue_number": 123
}
Response:
json
{
  "summary": "Add @jsx common parser issues in the docs...",
  "type": "feature_request",
  "priority_score": "3 - Useful improvement.",
  "suggested_labels": ["enhancement", "feature"],
  "potential_impact":"Can improve user experience or core capability."
}


