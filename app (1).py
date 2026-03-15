import streamlit as st
import json
import re
import requests
from groq import Groq

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DEEPSI — Civic AI Assistant",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=Noto+Serif:ital,wght@0,400;0,600;1,400&display=swap');
:root {
    --saffron: #FF6B00; --deep-blue: #0B1F4B; --chakra-blue: #1A3A7A;
    --gold: #D4A017; --cream: #FDF6EC; --ink: #1C1C2E;
    --muted: #6B7280; --border: rgba(212,160,23,0.25); --card-bg: rgba(255,255,255,0.97);
}
html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; background-color: var(--cream); color: var(--ink); }
.deepsi-header {
    background: linear-gradient(135deg, var(--deep-blue) 0%, var(--chakra-blue) 60%, #0D2B5E 100%);
    border-bottom: 3px solid var(--saffron);
    padding: 1.5rem 2rem; margin: -1rem -1rem 2rem -1rem; position: relative; overflow: hidden;
}
.deepsi-header::after {
    content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--saffron), var(--gold), #138808, var(--gold), var(--saffron));
}
.deepsi-title { font-family: 'Rajdhani', sans-serif; font-size: 2.6rem; font-weight: 700; color: white; letter-spacing: 0.08em; margin: 0; line-height: 1; }
.deepsi-title span { color: var(--saffron); }
.deepsi-subtitle { font-family: 'Noto Serif', serif; font-size: 0.85rem; color: rgba(255,255,255,0.65); letter-spacing: 0.15em; text-transform: uppercase; margin-top: 0.4rem; }
.tricolor-bar { display: flex; height: 4px; border-radius: 2px; overflow: hidden; margin-top: 1rem; width: 120px; }
.tricolor-bar div { flex: 1; }
.section-label { font-size: 0.7rem; font-weight: 700; letter-spacing: 0.2em; text-transform: uppercase; color: var(--saffron); margin-bottom: 0.5rem; }
.step-indicator { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; color: var(--muted); padding: 0.4rem 0; border-bottom: 1px dashed var(--border); margin-bottom: 0.3rem; }
.step-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--saffron); flex-shrink: 0; animation: pulse 1.5s infinite; }
@keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(0.7); } }
.stButton > button {
    background: linear-gradient(135deg, var(--saffron) 0%, #E55A00 100%) !important;
    color: white !important; border: none !important; border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important; font-size: 1.1rem !important;
    font-weight: 700 !important; letter-spacing: 0.08em !important;
    width: 100% !important; text-transform: uppercase !important;
    box-shadow: 0 4px 14px rgba(255,107,0,0.3) !important;
}
.stButton > button:hover { box-shadow: 0 6px 20px rgba(255,107,0,0.45) !important; }
</style>
""", unsafe_allow_html=True)

# ─── Location Data ─────────────────────────────────────────────────────────────
@st.cache_data
def load_location_data():
    try:
        import india
        sdmap = {}
        for attr in dir(india.cities):
            if attr.startswith("_"):
                continue
            try:
                city = getattr(india.cities, attr)
                if not hasattr(city, "state") or not hasattr(city, "name"):
                    continue
                s = str(city.state).replace("<State: ", "").replace(">", "").strip()
                c = str(city.name).strip()
                if s and c:
                    sdmap.setdefault(s, set()).add(c)
            except Exception:
                continue
        if sdmap:
            return {s: sorted(list(d)) for s, d in sorted(sdmap.items())}
    except Exception:
        pass
    # Full hardcoded fallback — all states + UTs
    return {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Kurnool", "Nellore"],
        "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat"],
        "Assam": ["Guwahati", "Dibrugarh", "Jorhat", "Silchar", "Tezpur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
        "Chhattisgarh": ["Raipur", "Bilaspur", "Durg", "Korba"],
        "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi", "Dwarka", "Rohini"],
        "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
        "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Rohtak"],
        "Himachal Pradesh": ["Shimla", "Dharamshala", "Mandi", "Solan"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Garhwa"],
        "Karnataka": ["Bangalore Urban", "Mysuru", "Hubli-Dharwad", "Mangaluru", "Belagavi", "Kalaburagi"],
        "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kannur", "Kollam"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane", "Aurangabad", "Solapur"],
        "Manipur": ["Imphal", "Churachandpur", "Thoubal"],
        "Meghalaya": ["Shillong", "Tura", "Jowai"],
        "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
        "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Sambalpur", "Berhampur"],
        "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner", "Alwar"],
        "Sikkim": ["Gangtok", "Namchi", "Mangan"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
        "Tripura": ["Agartala", "Udaipur", "Dharmanagar"],
        "Uttar Pradesh": ["Lucknow", "Varanasi", "Agra", "Prayagraj", "Kanpur", "Noida", "Meerut", "Ghaziabad", "Gorakhpur", "Mathura", "Aligarh"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Nainital"],
        "West Bengal": ["Kolkata", "Howrah", "Siliguri", "Asansol", "Durgapur", "Bardhaman"],
        "Jammu & Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
        "Ladakh": ["Leh", "Kargil"],
        "Chandigarh": ["Chandigarh"],
        "Puducherry": ["Puducherry", "Karaikal", "Yanam"],
    }

# ─── Constants ─────────────────────────────────────────────────────────────────
CATEGORIES = [
    "", "Urban Civic Infrastructure", "Sanitation & Waste", "Utilities",
    "Law & Public Safety", "Transport & Mobility",
    "Government Documents & Identity", "Land & Property",
    "Taxation & Finance", "Public Health & Healthcare",
    "Education & Public Institutions", "Governance & Administrative Complaints",
]

BLOCKED_DOMAINS = [
    "merriam-webster.com", "dictionary.com", "cambridge.org", "collinsdictionary.com",
    "wordreference.com", "vocabulary.com", "thefreedictionary.com", "yourdictionary.com",
    "wikipedia.org", "wiktionary.org", "britannica.com", "quora.com", "reddit.com",
    "youtube.com", "facebook.com", "twitter.com", "instagram.com",
    "amazon.com", "flipkart.com", "chronicleclub.in", "bombaysamachar.com", "iria.org",
]

BLOCKED_URL_PATTERNS = [
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    "nhrc.nic.in/assets", "rajyasabha.nic.in/UploadedFiles/Debates",
]

TRUSTED_DOMAINS  = ["gov.in", "nic.in", "india.gov.in", "mygov.in"]
KNOWN_GOV_DOMAINS = ["gov.in", "nic.in", "mygov.in", "india.gov.in",
                     "pgportal.gov.in", "umang.gov.in", "digilocker.gov.in"]

# Fast keyword-based jurisdiction detection
CENTRAL_KEYWORDS = [
    "passport", "visa", "aadhar", "aadhaar", "pan card", "pan number",
    "income tax", "itr", "railway", "train", "irctc", "airport", "flight",
    "epfo", "provident fund", "pf account", "post office", "speed post",
    "army", "defence", "rbi", "sebi", "gst", "customs", "central government",
    "nps", "national pension", "uidai",
]
STATE_KEYWORDS = [
    "police", "fir", "thana", "ration card", "state highway", "state road",
    "electricity board", "discom", "state electricity", "bijli board",
    "driving licence", "dl renewal", "rto", "vehicle registration",
    "district hospital", "government hospital", "civil hospital",
    "revenue", "land record", "patwari", "tehsildar", "naib tehsildar",
    "education board", "board exam", "high court", "state transport",
]

# ─── Pipeline Functions ────────────────────────────────────────────────────────

def analyze_query(problem, state, district, locality, category):
    return {
        "problem":  problem,
        "location": ", ".join(filter(None, [locality, district, state])),
        "category": category or "General",
        "state":    state,
        "district": district,
    }


def predict_jurisdiction(client, query):
    combined = (query["problem"] + " " + query["category"]).lower()

    # Instant keyword match — no API call needed
    if any(kw in combined for kw in CENTRAL_KEYWORDS):
        return "Central"
    if any(kw in combined for kw in STATE_KEYWORDS):
        return "State"

    # Ambiguous — ask LLM with strict system prompt
    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": (
                    "You classify Indian civic problems. "
                    "Reply with EXACTLY one word: Central, State, or Local.\n"
                    "Central = passport/aadhaar/railway/income tax/army/post office/EPFO/GST.\n"
                    "State = police/RTO/ration card/state PWD/electricity board/state hospital/land records.\n"
                    "Local = garbage/street light/water supply/drainage/local road/birth certificate/building permit/park.\n"
                    "Output one word only. No explanation."
                )},
                {"role": "user", "content": (
                    f"Problem: {query['problem']}\n"
                    f"Category: {query['category']}\n"
                    "Central, State, or Local?"
                )},
            ],
            max_tokens=5,
            temperature=0,
        )
        word = (resp.choices[0].message.content or "").strip().split()[0].strip(".,!?").capitalize()
        return word if word in ["Central", "State", "Local"] else "Local"
    except Exception:
        return "Local"


def generate_search_query(query, jurisdiction):
    district = query["district"]
    state    = query["state"]
    cat      = query["category"] if query["category"] not in ("", "General") else ""

    if cat:
        topic = cat
    else:
        stopwords = {"is","are","was","the","a","an","my","i","in","at","of","to",
                     "for","has","have","been","and","not","there","it","still",
                     "with","on","this","that","its","we","they","me","he","she"}
        words = [w for w in query["problem"].lower().split() if w not in stopwords]
        topic = " ".join(words[:4])

    if jurisdiction == "Central":
        return f"{topic} India central government ministry complaint portal"
    elif jurisdiction == "State":
        return f"{topic} {state} government department helpline complaint"
    else:
        return f"{topic} {district} {state} nagar nigam municipal corporation complaint"


def perform_search(search_query, serper_key, max_results=10):
    results = []
    try:
        resp = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": serper_key, "Content-Type": "application/json"},
            json={"q": search_query, "gl": "in", "hl": "en", "num": max_results},
            timeout=10,
        )
        data = resp.json()
        for item in data.get("organic", []):
            url   = item.get("link", "")
            title = item.get("title", "")
            body  = item.get("snippet", "")
            if any(bd in url for bd in BLOCKED_DOMAINS):
                continue
            if any(pat in url.lower() for pat in BLOCKED_URL_PATTERNS):
                continue
            if len(body.strip()) < 30:
                continue
            results.append({"href": url, "title": title, "body": body})
    except Exception:
        pass
    return results


def filter_domains(results):
    trusted = [r for r in results if any(d in r.get("href","") for d in TRUSTED_DOMAINS)]
    others  = [r for r in results if not any(d in r.get("href","") for d in TRUSTED_DOMAINS)]
    return (trusted + others)[:5]


def extract_page_content(url, timeout=6):
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        text = re.sub(r"<(script|style)[^>]*>.*?</(script|style)>", " ",
                      resp.text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text[:1500]
    except Exception:
        return ""


def build_context(filtered_results):
    parts, sources = [], []
    for r in filtered_results:
        url     = r.get("href", "")
        snippet = r.get("body", "")
        title   = r.get("title", "")
        content = snippet
        if any(d in url for d in TRUSTED_DOMAINS) and len(snippet) < 200:
            extracted = extract_page_content(url)
            if extracted:
                content = extracted[:800]
        if content:
            parts.append(f"[Source: {title}]\n{content}")
            sources.append(url)
    return "\n\n---\n\n".join(parts[:4]), sources


def generate_final_answer(client, query, jurisdiction, context):
    system = """You are DEEPSI, an expert Indian civic governance assistant.
Identify the exact responsible Indian government authority for the citizen's problem.
Be specific — name the actual department/body. Reference Indian law/governance hierarchy.

Return ONLY this format (no preamble, no extra text):

**Problem Summary:** <1 sentence>
**Responsible Authority:** <specific body e.g. Varanasi Nagar Nigam>
**Government Level:** <Central Government / State Government / Local Government>
**Department:** <specific dept e.g. Sanitation & Solid Waste Management>
**Reasoning:** <2-3 sentences on why this body is responsible under Indian governance>
**Suggested Action:** <one concrete step — name a portal or helpline e.g. pgportal.gov.in or call 1533>
**Official Website:** <one well-known working Indian govt URL — e.g. pgportal.gov.in, jansunwai.up.nic.in — DO NOT invent URLs>
**Sources Used:** <titles of Retrieved Context sources that informed your answer, or "Built-in knowledge">"""

    user = (
        f"Citizen Problem: {query['problem']}\n"
        f"Location: {query['location']}\n"
        f"Category: {query['category']}\n"
        f"Jurisdiction: {jurisdiction} Government\n\n"
        f"Retrieved Context:\n{context if context else 'No web context retrieved. Use your knowledge of Indian governance.'}\n\n"
        "Rules:\n"
        "- Ignore any non-Indian sources in context.\n"
        "- For Official Website, only use portals you are certain exist (gov.in / nic.in preferred).\n"
        "- In Sources Used, list only context source titles you actually used."
    )

    try:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            max_tokens=700,
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"**Problem Summary:** Could not generate answer.\n**Reasoning:** {e}"


def parse_answer(text):
    fields = {
        "Problem Summary": "", "Responsible Authority": "", "Government Level": "",
        "Department": "", "Reasoning": "", "Suggested Action": "",
        "Official Website": "", "Sources Used": "",
    }
    for key in fields:
        m = re.search(rf"\*\*{re.escape(key)}:\*\*\s*(.+?)(?=\n\*\*|\Z)", text, re.DOTALL)
        if m:
            fields[key] = m.group(1).strip()
    return fields


def clean(val):
    val = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", val.strip())
    val = re.sub(r"<[^>]+>", "", val)
    return val.strip()


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="deepsi-header">
    <div style="display:flex;align-items:center;gap:1.2rem;">
        <div style="font-size:3rem;line-height:1;">🏛️</div>
        <div>
            <div class="deepsi-title"><span>DEEP</span>SI</div>
            <div class="deepsi-subtitle">Democratic Engine for Empowering Public Service Inquiries</div>
            <div class="tricolor-bar">
                <div style="background:#FF6B00;"></div>
                <div style="background:#FFFFFF;"></div>
                <div style="background:#138808;"></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Load Data ─────────────────────────────────────────────────────────────────
location_data = load_location_data()
states = list(location_data.keys())

# ─── Layout ───────────────────────────────────────────────────────────────────
col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
    groq_key   = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    serper_key = st.text_input("Serper API Key (free at serper.dev)", type="password", placeholder="Enter Serper key...")
    st.caption("Serper = 2,500 free Google searches/month. Get key at serper.dev — no card needed.")

    st.markdown('<div class="section-label" style="margin-top:1rem;">📝 Problem Details</div>', unsafe_allow_html=True)
    problem = st.text_area(
        "Describe your civic problem",
        placeholder="e.g. My passport application is stuck for 3 months. No update from the passport office.",
        height=110,
    )

    c1, c2 = st.columns(2)
    with c1:
        selected_state = st.selectbox("State", options=["— Select State —"] + states)
    with c2:
        districts = location_data.get(selected_state, []) if selected_state != "— Select State —" else []
        selected_district = st.selectbox("District", options=["— Select District —"] + districts)

    locality = st.text_input("Locality / Area", placeholder="e.g. Sigra, Assi Ghat, Pandeypur")
    category = st.selectbox("Problem Category (optional)", options=CATEGORIES)

    st.markdown("<br>", unsafe_allow_html=True)
    submit = st.button("🔍 FIND RESPONSIBLE AUTHORITY", use_container_width=True)

# ─── Results ──────────────────────────────────────────────────────────────────
with col_result:
    st.markdown('<div class="section-label">📋 Analysis Result</div>', unsafe_allow_html=True)

    if submit:
        errors = []
        if not groq_key:            errors.append("Please enter your Groq API Key.")
        if not serper_key:          errors.append("Please enter your Serper API Key.")
        if not problem.strip():     errors.append("Please describe your civic problem.")
        if selected_state    == "— Select State —":    errors.append("Please select a state.")
        if selected_district == "— Select District —": errors.append("Please select a district.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                client   = Groq(api_key=groq_key)
                query    = analyze_query(problem, selected_state, selected_district, locality, category)
                progress = st.empty()

                def step(msg):
                    progress.markdown(
                        f'<div class="step-indicator"><div class="step-dot"></div>{msg}</div>',
                        unsafe_allow_html=True,
                    )

                step("Step 1 — Predicting jurisdiction…")
                jurisdiction = predict_jurisdiction(client, query)

                step("Step 2 — Building search query…")
                search_q = generate_search_query(query, jurisdiction)

                step("Step 3 — Searching (Serper / Google)…")
                raw_results = perform_search(search_q, serper_key)

                step("Step 4 — Filtering trusted sources…")
                filtered = filter_domains(raw_results)

                step("Step 5 — Extracting page content…")
                context, _ = build_context(filtered)

                step("Step 6 — Generating final answer…")
                answer_text = generate_final_answer(client, query, jurisdiction, context)
                parsed      = parse_answer(answer_text)
                progress.empty()

                authority    = clean(parsed.get("Responsible Authority", "—"))
                jlevel       = clean(parsed.get("Government Level") or f"{jurisdiction} Government")
                dept         = clean(parsed.get("Department", "—"))
                summary      = clean(parsed.get("Problem Summary", problem[:120]))
                reasoning    = clean(parsed.get("Reasoning", "—"))
                action       = clean(parsed.get("Suggested Action", "—"))
                official_url = clean(parsed.get("Official Website", ""))
                sources_used = clean(parsed.get("Sources Used", ""))

                import html as _html

                # Authority banner
                st.markdown(
                    f'<div style="background:#0B1F4B;color:white;padding:0.8rem 1.2rem;'
                    f'border-radius:8px;font-size:1.05rem;font-weight:700;margin-bottom:0.4rem;">'
                    f'🏛 {_html.escape(authority)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<span style="background:linear-gradient(135deg,#FF6B00,#D4A017);color:white;'
                    f'padding:0.25rem 1rem;border-radius:20px;font-size:0.78rem;font-weight:700;'
                    f'letter-spacing:0.1em;text-transform:uppercase;">'
                    f'{_html.escape(jlevel)}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.markdown(f"**📄 Problem Summary**\n\n{summary}")
                st.markdown(f"**🏢 Department:** {dept}")
                st.markdown(f"**🧠 Reasoning:** {reasoning}")
                st.success(f"✅ Suggested Action: {action}")

                # Only show URL if it's a verified gov domain
                if official_url and official_url.startswith("http") and any(d in official_url for d in KNOWN_GOV_DOMAINS):
                    st.markdown(f"**🔗 Official Portal:** [{official_url}]({official_url})")

                # Pipeline trace
                kw_match = any(kw in (problem + category).lower() for kw in CENTRAL_KEYWORDS + STATE_KEYWORDS)
                with st.expander("🧩 How this answer was generated"):
                    src_list = "\n".join(
                        f"- **{r.get('title','Untitled')}**  \n"
                        f"  {r.get('href','')}  \n"
                        f"  _{r.get('body','')[:120]}..._"
                        for r in filtered[:5]
                    ) or "⚠️ No sources retrieved."

                    ctx_note = (
                        f"✅ {len(context)} characters extracted from sources."
                        if context else
                        "⚠️ No content extracted — LLM used built-in knowledge of Indian governance."
                    )

                    st.markdown(f"""
#### Step 1 — Jurisdiction Prediction
{'🔑 Detected via keyword match' if kw_match else '🤖 Classified by LLM (openai/gpt-oss-20b)'} → **{jurisdiction} Government**

#### Step 2 — Web Search (Serper / Google)
Query: `{search_q}`
Results found: **{len(raw_results)}** (after filtering irrelevant domains)

#### Step 3 — Retrieved Sources
{src_list}

#### Step 4 — Context Extraction
{ctx_note}

#### Step 5 — LLM Final Reasoning (openai/gpt-oss-120b)
Given: problem description, location, jurisdiction, and retrieved context.
Output: responsible authority, department, reasoning, suggested action, official portal.

**Sources cited by LLM:** {sources_used or "Built-in knowledge"}
""")

            except Exception as ex:
                st.error(f"Error: {ex}")
                st.info("Check your Groq and Serper API keys and try again.")
    else:
        st.markdown("""
<div style="background:rgba(11,31,75,0.04);border:1px dashed rgba(212,160,23,0.4);
    border-radius:8px;padding:2.5rem 2rem;text-align:center;margin-top:1rem;">
    <div style="font-size:3rem;margin-bottom:0.8rem;">🏛️</div>
    <div style="font-family:'Rajdhani',sans-serif;font-size:1.1rem;font-weight:600;
        color:#374151;letter-spacing:0.05em;">
        Fill in your details and click<br>
        <span style="color:#FF6B00;">FIND RESPONSIBLE AUTHORITY</span>
    </div>
    <div style="margin-top:1rem;font-size:0.78rem;color:#9CA3AF;letter-spacing:0.1em;text-transform:uppercase;">
        Powered by Groq · Serper · Indian Governance AI
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:rgba(212,160,23,0.25);margin-top:3rem;">
<div style="text-align:center;font-size:0.75rem;color:#9CA3AF;padding:0.5rem 0;letter-spacing:0.08em;">
    DEEPSI · Democratic Engine for Empowering Public Service Inquiries · India 🇮🇳
</div>
""", unsafe_allow_html=True)
