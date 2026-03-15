# ⚖️ LexIndia – AI Legal Assistant

A sophisticated AI-powered legal chatbot for Indian law, built with Streamlit + Groq.

## Features

- 🏛️ **Covers**: BNS 2023, BNSS 2023, BSA 2023, Indian Constitution, CPC, Contract Law, Family Law, Labour Law, RERA, RTI, IP Law, Consumer Law & more
- 💬 **ChatGPT-style UI**: Sidebar with conversation history + full chat interface
- 🧠 **Conversation memory**: Full context window maintained per conversation
- 🔒 **Secure**: Groq API key stored only in session (never persisted)
- ⚡ **Fast**: Powered by Llama 3.3 70B via Groq's ultra-fast inference

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

## Getting a Groq API Key

1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up / log in (free tier available)
3. Create a new API key
4. Paste it in the app sidebar

## Usage

1. Launch the app → enter your Groq API key in the sidebar
2. Click "New Conversation" or use the sample question buttons
3. Ask any legal question — the bot will cite specific sections and articles
4. All conversations are saved in the sidebar for reference during your session

## Legal Coverage

| Category | Laws Covered |
|----------|-------------|
| Criminal | BNS 2023, BNSS 2023 (replaces IPC & CrPC) |
| Evidence | BSA 2023 (replaces Indian Evidence Act) |
| Constitutional | All Articles, Amendments, Fundamental Rights |
| Civil | CPC, Contract Act, Specific Relief Act |
| Family | Hindu Marriage Act, Muslim Personal Law, Domestic Violence Act |
| Property | Transfer of Property Act, RERA 2016, Registration Act |
| Labour | Labour Codes 2020, POSH Act |
| IP | Patents Act, Copyright Act, Trade Marks Act |
| Consumer | Consumer Protection Act 2019 |
| Information | RTI Act 2005 |

## Disclaimer

LexIndia provides general legal information only. For specific legal advice, always consult a qualified advocate registered with the Bar Council of India.
