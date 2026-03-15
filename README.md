# D

A civic AI assistant that helps Indian citizens identify the correct government authority
responsible for their civic problem, using LLM reasoning + live web search.

---

## 🚀 Quick Start

### 1. Clone / Download
```bash
git clone <repo>
cd deepsi
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 🔑 Prerequisites

- **Groq API Key** — Free at https://console.groq.com
  - Used for LLaMA 3 inference (fast & free tier available)

---

## 🏗️ System Pipeline

```
User Input
    │
    ▼
[1] analyze_query()        — Structure the problem + location
    │
    ▼
[2] predict_jurisdiction() — LLM decides: Central / State / Local
    │
    ▼
[3] generate_search_query()— Build a targeted web search string
    │
    ▼
[4] perform_search()       — DuckDuckGo search (no API key needed)
    │
    ▼
[5] filter_domains()       — Prioritise gov.in / nic.in sources
    │
    ▼
[6] extract_page_content() — trafilatura extracts clean text
    │
    ▼
[7] build_context()        — Assemble top 4 sources into context
    │
    ▼
[8] generate_final_answer()— LLaMA 3 70B reasons over context
    │
    ▼
Structured Output (Authority, Level, Dept, Action, Sources)
```

---

## 📁 Project Structure

```
deepsi/
├── app.py                  # Main Streamlit app (all logic + UI)
├── requirements.txt
└── README.md
```

Location data is loaded from the `indian-cities-json` package — no large JSON files needed.

---

## 🏛️ Governance Hierarchy Supported

| Level    | Examples                                              |
|----------|-------------------------------------------------------|
| Central  | Passport, Aadhaar, Railways, Income Tax, EPFO         |
| State    | Police, State PWD, Ration Card, State Electricity     |
| Local    | Garbage, Street Lights, Water Supply, Birth Cert      |

---

## ⚙️ Models Used

| Task                | Model             |
|---------------------|-------------------|
| Jurisdiction Predict| llama3-8b-8192    |
| Final Answer        | llama3-70b-8192   |

Both via **Groq API** (fast inference, free tier).
