import streamlit as st
import json
import re
import requests
from groq import Groq
from duckduckgo_search import DDGS
import trafilatura

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
    --saffron: #FF6B00;
    --deep-blue: #0B1F4B;
    --chakra-blue: #1A3A7A;
    --gold: #D4A017;
    --cream: #FDF6EC;
    --ink: #1C1C2E;
    --muted: #6B7280;
    --border: rgba(212,160,23,0.25);
    --success: #16A34A;
    --card-bg: rgba(255,255,255,0.97);
}

html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    background-color: var(--cream);
    color: var(--ink);
}

/* Ashoka Chakra watermark */
.stApp::before {
    content: "⊕";
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 600px;
    color: rgba(255, 107, 0, 0.03);
    pointer-events: none;
    z-index: 0;
}

/* Header */
.deepsi-header {
    background: linear-gradient(135deg, var(--deep-blue) 0%, var(--chakra-blue) 60%, #0D2B5E 100%);
    border-bottom: 3px solid var(--saffron);
    padding: 1.5rem 2rem;
    margin: -1rem -1rem 2rem -1rem;
    position: relative;
    overflow: hidden;
}
.deepsi-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--saffron), var(--gold), #138808, var(--gold), var(--saffron));
}
.deepsi-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: white;
    letter-spacing: 0.08em;
    margin: 0;
    line-height: 1;
}
.deepsi-title span { color: var(--saffron); }
.deepsi-subtitle {
    font-family: 'Noto Serif', serif;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.65);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 0.4rem;
}
.tricolor-bar {
    display: flex;
    height: 4px;
    border-radius: 2px;
    overflow: hidden;
    margin-top: 1rem;
    width: 120px;
}
.tricolor-bar div { flex: 1; }

/* Cards */
.form-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.section-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--saffron);
    margin-bottom: 0.5rem;
}

/* Result block */
.result-card {
    background: var(--card-bg);
    border-left: 4px solid var(--saffron);
    border-radius: 4px 8px 8px 4px;
    padding: 1.5rem;
    margin-top: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}
.authority-badge {
    display: inline-block;
    background: var(--deep-blue);
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-bottom: 0.5rem;
}
.gov-level {
    display: inline-block;
    background: linear-gradient(135deg, var(--saffron), var(--gold));
    color: white;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-left: 0.5rem;
}
.source-chip {
    display: inline-block;
    background: rgba(11,31,75,0.07);
    border: 1px solid var(--border);
    color: var(--chakra-blue);
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.75rem;
    margin: 0.2rem;
    text-decoration: none;
    font-weight: 500;
}
.step-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.78rem;
    color: var(--muted);
    padding: 0.4rem 0;
    border-bottom: 1px dashed var(--border);
    margin-bottom: 0.3rem;
}
.step-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--saffron);
    flex-shrink: 0;
    animation: pulse 1.5s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.7); }
}

/* Streamlit overrides */
.stTextArea textarea, .stTextInput input, .stSelectbox select {
    border-radius: 6px !important;
    border-color: var(--border) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
}
.stButton > button {
    background: linear-gradient(135deg, var(--saffron) 0%, #E55A00 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(255,107,0,0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(255,107,0,0.45) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Load Location Data ────────────────────────────────────────────────────────
@st.cache_data
def load_location_data():
    try:
        import india
        state_district_map = {}
        # Iterate all cities and group districts by state name
        for attr in dir(india.cities):
            if attr.startswith("_"):
                continue
            try:
                city = getattr(india.cities, attr)
                if not hasattr(city, "state") or not hasattr(city, "name"):
                    continue
                state_name = str(city.state).replace("<State: ", "").replace(">", "").strip()
                city_name  = str(city.name).strip()
                if state_name and city_name:
                    state_district_map.setdefault(state_name, set()).add(city_name)
            except Exception:
                continue
        if state_district_map:
            return {s: sorted(list(d)) for s, d in sorted(state_district_map.items())}
        raise ValueError("empty")
    except Exception:
        # Fallback: try local JSON file
        try:
            with open("states_districts.json") as f:
                return json.load(f)
        except Exception:
            # Minimal hardcoded fallback so the app still runs
            return {
                "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Tirupati"],
                "Delhi": ["Central Delhi", "East Delhi", "New Delhi", "North Delhi", "South Delhi", "West Delhi"],
                "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot"],
                "Karnataka": ["Bangalore Urban", "Mysuru", "Hubli-Dharwad", "Mangaluru"],
                "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur"],
                "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur"],
                "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Thane"],
                "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
                "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli"],
                "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"],
                "Uttar Pradesh": ["Lucknow", "Varanasi", "Agra", "Prayagraj", "Kanpur", "Noida", "Meerut"],
                "West Bengal": ["Kolkata", "Howrah", "Siliguri", "Asansol"],
            }

# ─── Pipeline Functions ────────────────────────────────────────────────────────

def analyze_query(problem: str, state: str, district: str, locality: str, category: str) -> dict:
    return {
        "problem": problem,
        "location": f"{locality}, {district}, {state}",
        "category": category or "General",
        "state": state,
        "district": district,
    }


def predict_jurisdiction(client: Groq, query: dict) -> str:
    prompt = f"""You are an Indian governance expert.
Given this civic problem: "{query['problem']}"
Category: {query['category']}
Location: {query['location']}

Respond with ONLY one word — the government level responsible:
Central / State / Local

Examples:
- Passport, Aadhar, Railway, Income Tax → Central
- Police, State road, Education board, Ration card → State
- Garbage, Street light, Water supply, Birth certificate, Local road → Local"""
    
    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=20,
        temperature=0,
    )
    try:
        raw = resp.choices[0].message.content or ""
        words = raw.strip().split()
        level = words[0].capitalize() if words else "Local"
    except (IndexError, AttributeError):
        level = "Local"
    return level if level in ["Central", "State", "Local"] else "Local"


# Domains that are never useful for civic governance queries
BLOCKED_DOMAINS = [
    "merriam-webster.com", "dictionary.com", "cambridge.org",
    "collinsdictionary.com", "wordreference.com", "vocabulary.com",
    "thefreedictionary.com", "macmillandictionary.com", "yourdictionary.com",
    "wikipedia.org", "wiktionary.org", "britannica.com",
    "quora.com", "reddit.com", "youtube.com", "facebook.com",
    "twitter.com", "instagram.com", "amazon.com", "flipkart.com",
]

TRUSTED_DOMAINS = [
    "gov.in", "nic.in", "india.gov.in", "mygov.in",
    "mohua.gov.in", "jansunwai.up.nic.in",
]

def generate_search_query(query: dict, jurisdiction: str) -> str:
    # Build a concrete, civic-specific query — avoid generic words like "responsible"
    problem_short = query["problem"][:80].strip()
    district = query["district"]
    state = query["state"]
    cat = query["category"] if query["category"] not in ("", "General") else ""

    if jurisdiction == "Central":
        prefix = "central government ministry department India"
    elif jurisdiction == "State":
        prefix = f"{state} government department"
    else:
        prefix = f"municipal corporation nagar palika {district} {state}"

    parts = [prefix, problem_short]
    if cat:
        parts.append(cat)
    parts.append("complaint redressal India")
    return " ".join(parts)


def perform_search(search_query: str, max_results: int = 10) -> list:
    results = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(search_query, max_results=max_results):
                url = r.get("href", "")
                # Drop blocked domains immediately at fetch time
                if not any(bd in url for bd in BLOCKED_DOMAINS):
                    results.append(r)
    except Exception:
        pass
    return results


def filter_domains(results: list) -> list:
    trusted, others = [], []
    for r in results:
        url = r.get("href", "")
        if any(d in url for d in TRUSTED_DOMAINS):
            trusted.append(r)
        else:
            others.append(r)
    # Prefer trusted gov sources; fall back to others only if needed
    combined = trusted + others
    return combined[:5]


def extract_page_content(url: str, timeout: int = 6) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DEEPSI-Bot/1.0)"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        text = trafilatura.extract(resp.text, include_comments=False, include_tables=False)
        return (text or "")[:1500]
    except Exception:
        return ""


def build_context(filtered_results: list) -> tuple[str, list]:
    context_parts, sources = [], []
    for r in filtered_results:
        url = r.get("href", "")
        snippet = r.get("body", "")
        title = r.get("title", "")
        
        # Use snippet first; try full extraction for .gov.in
        content = snippet
        if any(d in url for d in ["gov.in", "nic.in"]) and len(snippet) < 200:
            extracted = extract_page_content(url)
            if extracted:
                content = extracted[:800]
        
        if content:
            context_parts.append(f"[Source: {title}]\n{content}")
            sources.append(url)
    
    return "\n\n---\n\n".join(context_parts[:4]), sources


def generate_final_answer(client: Groq, query: dict, jurisdiction: str, context: str) -> str:
    system = """You are DEEPSI, an expert Indian civic governance assistant.
Your task: identify the exact responsible government authority for the citizen's problem.
Be specific. Name the actual department/body. Reference Indian governance hierarchy.
Return ONLY this structured format (no preamble):

**Problem Summary:** <1 sentence>
**Responsible Authority:** <specific body name>
**Government Level:** <Central / State / Local Government>
**Department:** <specific department>
**Reasoning:** <2-3 sentences explaining why>
**Suggested Action:** <concrete next step for the citizen>"""

    user = f"""Citizen Problem: {query['problem']}
Location: {query['location']}
Category: {query['category']}
Predicted Jurisdiction: {jurisdiction} Government

Retrieved Context:
{context or 'No context available. Use your knowledge of Indian governance.'}

Identify the responsible authority and provide actionable guidance."""

    resp = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=600,
        temperature=0.2,
    )
    try:
        return (resp.choices[0].message.content or "").strip()
    except (IndexError, AttributeError):
        return "Unable to generate answer. Please try again."


# ─── Parse Answer ──────────────────────────────────────────────────────────────
def parse_answer(text: str) -> dict:
    fields = {
        "Problem Summary": "",
        "Responsible Authority": "",
        "Government Level": "",
        "Department": "",
        "Reasoning": "",
        "Suggested Action": "",
    }
    for key in fields:
        pattern = rf"\*\*{key}:\*\*\s*(.+?)(?=\n\*\*|\Z)"
        m = re.search(pattern, text, re.DOTALL)
        if m:
            fields[key] = m.group(1).strip()
    return fields


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="deepsi-header">
    <div style="display:flex; align-items:center; gap:1.2rem;">
        <div style="font-size:3rem; line-height:1;">🏛️</div>
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

CATEGORIES = [
    "", "Urban Civic Infrastructure", "Sanitation & Waste", "Utilities",
    "Law & Public Safety", "Transport & Mobility",
    "Government Documents & Identity", "Land & Property",
    "Taxation & Finance", "Public Health & Healthcare",
    "Education & Public Institutions", "Governance & Administrative Complaints",
]

# ─── Layout ───────────────────────────────────────────────────────────────────
col_form, col_result = st.columns([1, 1.2], gap="large")

with col_form:
    st.markdown('<div class="section-label">🔑 API Configuration</div>', unsafe_allow_html=True)
    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")

    st.markdown('<div class="section-label" style="margin-top:1rem;">📝 Problem Details</div>', unsafe_allow_html=True)
    problem = st.text_area(
        "Describe your civic problem",
        placeholder="e.g. There is a broken street light outside my house for the past 3 weeks. Nobody has come to fix it.",
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

# ─── Processing & Results ─────────────────────────────────────────────────────
with col_result:
    st.markdown('<div class="section-label">📋 Analysis Result</div>', unsafe_allow_html=True)

    if submit:
        # Validation
        errors = []
        if not groq_key:
            errors.append("Please enter your Groq API Key.")
        if not problem.strip():
            errors.append("Please describe your civic problem.")
        if selected_state == "— Select State —":
            errors.append("Please select a state.")
        if selected_district == "— Select District —":
            errors.append("Please select a district.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            try:
                client = Groq(api_key=groq_key)
                query = analyze_query(problem, selected_state, selected_district, locality, category)

                progress_box = st.empty()

                def show_step(msg):
                    progress_box.markdown(
                        f'<div class="step-indicator"><div class="step-dot"></div>{msg}</div>',
                        unsafe_allow_html=True,
                    )

                show_step("Step 1 — Predicting jurisdiction level…")
                jurisdiction = predict_jurisdiction(client, query)

                show_step("Step 2 — Generating search query…")
                search_q = generate_search_query(query, jurisdiction)

                show_step("Step 3 — Searching the web…")
                raw_results = perform_search(search_q)

                show_step("Step 4 — Filtering trusted government sources…")
                filtered = filter_domains(raw_results)

                show_step("Step 5 — Extracting page content…")
                context, sources = build_context(filtered)

                show_step("Step 6 — Generating final authority analysis…")
                answer_text = generate_final_answer(client, query, jurisdiction, context)
                parsed = parse_answer(answer_text)

                progress_box.empty()

                # ── Sanitise parsed fields (strip markdown bold, stray HTML tags) ──
                import html as _html
                def clean(val: str) -> str:
                    import re as _re
                    val = val.strip()
                    val = _re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", val)   # remove **bold** / *italic*
                    val = _re.sub(r"<[^>]+>", "", val)                      # strip any HTML tags
                    return val.strip()

                jlevel    = clean(parsed.get("Government Level") or jurisdiction + " Government")
                authority = clean(parsed.get("Responsible Authority", "—"))
                dept      = clean(parsed.get("Department", "—"))
                summary   = clean(parsed.get("Problem Summary", problem[:120]))
                reasoning = clean(parsed.get("Reasoning", "—"))
                action    = clean(parsed.get("Suggested Action", "—"))

                # ── Render using native Streamlit (no raw HTML interpolation) ──
                st.markdown(
                    f'''<div style="background:#0B1F4B;color:white;padding:0.7rem 1.1rem;border-radius:6px;font-size:1rem;font-weight:600;margin-bottom:0.5rem;">
                    🏛 {_html.escape(authority)}</div>''',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'''<span style="background:linear-gradient(135deg,#FF6B00,#D4A017);color:white;padding:0.2rem 0.9rem;border-radius:20px;font-size:0.78rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">{_html.escape(jlevel)}</span>''',
                    unsafe_allow_html=True,
                )
                st.markdown("---")
                st.markdown(f"**📄 Summary**\n\n{summary}")
                st.markdown(f"**🏢 Department:** {dept}")
                st.markdown(f"**🧠 Reasoning:** {reasoning}")
                st.success(f"✅ Suggested Action: {action}")

                if sources:
                    st.markdown("**🔗 Sources**")
                    for s in sources[:6]:
                        st.markdown(f"- [{s}]({s})")

                with st.expander("🔎 Search Query Used"):
                    st.code(search_q)

            except Exception as ex:
                st.error(f"Error: {ex}")
                st.info("Check your Groq API key and internet connection.")
    else:
        st.markdown("""
<div style="
    background: rgba(11,31,75,0.04);
    border: 1px dashed rgba(212,160,23,0.4);
    border-radius: 8px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin-top: 1rem;
">
    <div style="font-size:3rem; margin-bottom:0.8rem;">🏛️</div>
    <div style="font-family:'Rajdhani',sans-serif; font-size:1.1rem; font-weight:600; color:#374151; letter-spacing:0.05em;">
        Fill in your details and click<br>
        <span style="color:var(--saffron);">FIND RESPONSIBLE AUTHORITY</span>
    </div>
    <div style="margin-top:1rem; font-size:0.78rem; color:#9CA3AF; letter-spacing:0.1em; text-transform:uppercase;">
        Powered by Groq · LLaMA 3 · DuckDuckGo
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:var(--border); margin-top:3rem;">
<div style="text-align:center; font-size:0.75rem; color:#9CA3AF; padding:0.5rem 0; letter-spacing:0.08em;">
    DEEPSI · Democratic Engine for Empowering Public Service Inquiries · India 🇮🇳
</div>
""", unsafe_allow_html=True)
