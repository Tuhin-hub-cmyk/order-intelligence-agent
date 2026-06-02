# Order Intelligence Agent ⚙️

> An AI-powered prototype that automates the analysis of open SAP 
> sales and service orders for the Atlas Copco Vacuum Technique 
> Australia customer care team.

## The Problem

Customer care teams manually review dozens of open SAP orders every 
morning to identify delays, blocked orders, and at-risk deliveries. 
This process is slow, error-prone, and relies on individual knowledge 
rather than a shared, always-up-to-date view.

## The Solution

A three-layer automated pipeline:
SAP Export → [Data Layer] → [Analysis Layer] → [AI Agent Layer]
↓
Web Dashboard + Natural Language Answers

1. **Data Layer** — Ingests SAP order exports and parses all date 
   fields automatically
2. **Analysis Layer** — Flags every order as OVERDUE, BLOCKED, 
   AT_RISK, STALE, or ON_TRACK and calculates total value at risk
3. **AI Layer** — Answers natural language questions like 
   *"Which orders are blocked?"* or 
   *"What should James focus on today?"*

## Features

- Automated order risk flagging across 6 categories
- Live summary dashboard with value-at-risk in AUD
- Top 5 priority orders ranked by urgency
- Natural language Q&A powered by Llama 3.1 via Groq
- Colour-coded web dashboard built with Streamlit
- Conversation memory across follow-up questions
- One-click data refresh

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core application logic |
| Pandas | Data loading and transformation |
| Groq API (Llama 3.1) | Free, fast AI inference |
| Streamlit | Web dashboard interface |
| python-dotenv | Environment variable management |

## Setup

### 1. Clone the repository
\```bash
git clone https://github.com/Tuhin-hub-cmyk/order-intelligence-agent.git
cd order-intelligence-agent
\```

### 2. Install dependencies
\```bash
pip install -r requirements.txt
\```

### 3. Add your API key

Create a `.env` file in the root folder:
\```
GROQ_API_KEY=your_groq_api_key_here
\```
Get a free key at [console.groq.com](https://console.groq.com) — 
no credit card required.

### 4. Run the web app
\```bash
streamlit run app.py
\```

Or run the terminal version:
\```bash
python main.py
\```

## Example Questions

| Question | What it demonstrates |
|---|---|
| *"Which orders need attention today?"* | Urgent order identification |
| *"What is blocking the Woodside Energy order?"* | Root cause analysis |
| *"Who has the most urgent workload — Sarah or James?"* | Team workload comparison |
| *"Summarise all overdue orders and delay reasons"* | Overdue order reporting |
| *"Which orders are escalated and what needs to happen?"* | Escalation management |

## Project Structure

\```
order-intelligence-agent/
├── data/
│   └── mock_orders.csv        ← Mock SAP sales and service orders
├── src/
│   ├── __init__.py
│   ├── data_loader.py         ← CSV loading and date parsing
│   ├── analyzer.py            ← Automated flagging and risk calc
│   └── agent.py               ← Groq AI natural language agent
├── app.py                     ← Streamlit web dashboard
├── main.py                    ← Terminal interface
├── requirements.txt
├── .env.example
└── .gitignore
\```

## Context

Built as a working prototype for the **Atlas Copco Group AI & 
Automation Internship** — Vacuum Technique Business Area, Australia.

Demonstrates how SAP order data can be automated into a live 
intelligence dashboard with AI-powered natural language querying — 
reducing manual checking time and improving customer care response.

---

**Author:** T M Towhidur Rahman Tuhin  
**Degree:** Bachelor of Commerce (Business Information Systems) 
— Curtin University, Perth WA