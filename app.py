import streamlit as st
import json
import time
import uuid
from datetime import datetime
from groq import Groq

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LexIndia – Legal Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root variables ── */
:root {
  --bg-primary:   #0a0c10;
  --bg-secondary: #111420;
  --bg-card:      #161b27;
  --bg-hover:     #1e2433;
  --accent-gold:  #c9a84c;
  --accent-dim:   #8a6f2e;
  --accent-glow:  rgba(201,168,76,0.15);
  --text-primary: #e8e4d9;
  --text-muted:   #7a7d8a;
  --text-faint:   #4a4d5a;
  --border:       rgba(201,168,76,0.15);
  --border-hover: rgba(201,168,76,0.35);
  --user-bubble:  #1a2035;
  --ai-bubble:    #111420;
  --radius:       12px;
  --shadow:       0 4px 24px rgba(0,0,0,0.4);
}

/* ── Global reset ── */
* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg-primary) !important;
  font-family: 'Inter', sans-serif !important;
  color: var(--text-primary) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: var(--bg-secondary) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── Main content ── */
[data-testid="stMainBlockContainer"] {
  padding: 0 !important;
  max-width: 100% !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--accent-dim); border-radius: 2px; }

/* ── Buttons ── */
.stButton > button {
  background: transparent !important;
  color: var(--text-muted) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  padding: 6px 14px !important;
  transition: all 0.2s ease !important;
  width: 100% !important;
}
.stButton > button:hover {
  background: var(--accent-glow) !important;
  border-color: var(--border-hover) !important;
  color: var(--accent-gold) !important;
}

/* ── Text input / text area ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: var(--bg-card) !important;
  color: var(--text-primary) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
  padding: 12px 16px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--accent-gold) !important;
  box-shadow: 0 0 0 2px var(--accent-glow) !important;
  outline: none !important;
}

/* ── Labels ── */
.stTextInput label, .stTextArea label {
  color: var(--text-muted) !important;
  font-size: 12px !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}

/* ── Chat input ── */
[data-testid="stChatInput"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
}
[data-testid="stChatInput"] textarea {
  background: transparent !important;
  color: var(--text-primary) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 14px !important;
}
[data-testid="stChatInput"] button {
  color: var(--accent-gold) !important;
}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {
  background: transparent !important;
  border: none !important;
  padding: 8px 0 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent-gold) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 8px 0 !important; }

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-primary) !important;
  border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SYSTEM PROMPT
# ══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """You are LexIndia, an expert AI legal assistant specializing in Indian law. You have comprehensive, up-to-date knowledge of:

**Core Legal Frameworks:**
- The Constitution of India (all articles, schedules, amendments up to 2024)
- Bharatiya Nyaya Sanhita (BNS) 2023 – replacing IPC 1860
- Bharatiya Nagarik Suraksha Sanhita (BNSS) 2023 – replacing CrPC 1973
- Bharatiya Sakshya Adhiniyam (BSA) 2023 – replacing Indian Evidence Act 1872

**Civil & Commercial Laws:**
- Code of Civil Procedure (CPC) 1908 and amendments
- Indian Contract Act 1872, Specific Relief Act 1963
- Transfer of Property Act 1882
- Companies Act 2013 and SEBI regulations
- Consumer Protection Act 2019
- RTI Act 2005

**Family & Personal Laws:**
- Hindu Marriage Act, Hindu Succession Act, Hindu Adoption & Maintenance Act
- Muslim Personal Law (Application of Shariat) Act 1937
- Special Marriage Act 1954
- Domestic Violence Act 2005, Dowry Prohibition Act 1961

**Labour & Employment:**
- Labour Codes 2020 (Wage Code, Industrial Relations Code, Social Security Code, OSH Code)
- POSH Act 2013

**Property & Land:**
- Registration Act 1908, Stamp Act
- Real Estate (RERA) Act 2016
- Land Acquisition Act 2013

**Intellectual Property:**
- Patents Act 1970, Copyright Act 1957, Trade Marks Act 1999

**Key Judicial Precedents & Landmark Cases**

**Response Guidelines:**
1. Always cite specific sections, articles, or provisions (e.g., "Section 103 BNS", "Article 21 Constitution", "Section 63 BSA")
2. Distinguish between old law (IPC/CrPC/Evidence Act) and new law (BNS/BNSS/BSA) when relevant
3. For BNS/BNSS/BSA, always mention both the new section AND the corresponding old section for clarity
4. Structure answers clearly: legal provision → explanation → practical implications
5. Mention relevant landmark Supreme Court / High Court judgments where applicable
6. Include important timelines, limitations periods, and procedural steps
7. Add a disclaimer for complex matters requiring professional legal counsel
8. Use simple language alongside legal terminology for accessibility
9. If asked about penalties, mention both imprisonment terms and fine amounts
10. For constitutional matters, reference fundamental rights, directive principles, and constitutional remedies

**Format your responses with:**
- **Bold** for section numbers and important terms
- Clear numbered lists for procedures/steps
- Brief case citations in italics
- A "⚠️ Note" for important caveats or disclaimers

You are knowledgeable, precise, and helpful. You do not provide advice that could be construed as inciting illegal activity. Always encourage consulting a qualified lawyer for specific legal matters."""


# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "groq_api_key": "",
        "api_key_valid": False,
        "conversations": {},      # id → {title, messages, created_at}
        "active_conv_id": None,
        "show_api_input": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def new_conversation():
    cid = str(uuid.uuid4())[:8]
    st.session_state.conversations[cid] = {
        "title": "New Conversation",
        "messages": [],
        "created_at": datetime.now().strftime("%d %b, %H:%M"),
    }
    st.session_state.active_conv_id = cid
    return cid


def get_active():
    cid = st.session_state.active_conv_id
    if cid and cid in st.session_state.conversations:
        return st.session_state.conversations[cid]
    return None


def auto_title(text: str) -> str:
    """Generate a short title from the first user message."""
    words = text.strip().split()
    title = " ".join(words[:6])
    return title[:40] + ("…" if len(title) > 40 else "")


def validate_key(api_key: str) -> bool:
    try:
        client = Groq(api_key=api_key)
        client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "hi"}],
            max_tokens=5,
        )
        return True
    except Exception:
        return False


def chat_with_groq(messages: list, api_key: str):
    client = Groq(api_key=api_key)
    groq_msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in messages:
        groq_msgs.append({"role": m["role"], "content": m["content"]})

    stream = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=groq_msgs,
        max_tokens=2048,
        temperature=0.3,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar():
    with st.sidebar:
        # ── Logo / Brand ──
        st.markdown("""
        <div style="padding: 24px 20px 16px; border-bottom: 1px solid rgba(201,168,76,0.15);">
          <div style="display:flex; align-items:center; gap:10px; margin-bottom:4px;">
            <span style="font-size:26px;">⚖️</span>
            <span style="font-family:'Playfair Display',serif; font-size:22px; font-weight:700;
                         background: linear-gradient(135deg,#c9a84c,#e8d5a3); -webkit-background-clip:text;
                         -webkit-text-fill-color:transparent; letter-spacing:0.02em;">LexIndia</span>
          </div>
          <div style="font-size:11px; color:#7a7d8a; letter-spacing:0.08em; text-transform:uppercase;
                      padding-left:36px;">AI Legal Assistant</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        # ── API Key section ──
        if not st.session_state.api_key_valid:
            st.markdown("""
            <div style="padding:0 16px; margin-bottom:8px;">
              <div style="font-size:11px; color:#7a7d8a; letter-spacing:0.06em; text-transform:uppercase;
                          margin-bottom:8px;">Groq API Key</div>
            </div>
            """, unsafe_allow_html=True)
            with st.container():
                api_input = st.text_input(
                    "API Key",
                    type="password",
                    placeholder="gsk_...",
                    label_visibility="collapsed",
                    key="api_key_input_field"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Connect", key="connect_btn"):
                        if api_input:
                            with st.spinner("Validating…"):
                                if validate_key(api_input):
                                    st.session_state.groq_api_key = api_input
                                    st.session_state.api_key_valid = True
                                    st.success("✓ Connected")
                                    time.sleep(0.8)
                                    st.rerun()
                                else:
                                    st.error("Invalid key")
                        else:
                            st.warning("Enter a key")
                with col2:
                    st.markdown("""
                    <a href="https://console.groq.com/keys" target="_blank"
                       style="display:block; text-align:center; padding:6px; font-size:12px;
                              color:#7a7d8a; text-decoration:none; border:1px solid rgba(201,168,76,0.15);
                              border-radius:8px; margin-top:1px;">
                      Get Key ↗
                    </a>
                    """, unsafe_allow_html=True)

            st.markdown("""
            <div style="padding:12px 16px; margin:8px 0; background:rgba(201,168,76,0.05);
                        border:1px solid rgba(201,168,76,0.12); border-radius:10px;">
              <div style="font-size:11px; color:#8a7a5a; line-height:1.6;">
                🔒 Your key is stored only in this session and never sent to any server other than Groq.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Connected status
            st.markdown("""
            <div style="padding:8px 16px; margin-bottom:4px; display:flex; align-items:center;
                        gap:8px; background:rgba(201,168,76,0.06); border-radius:8px; margin:0 4px 12px;">
              <span style="color:#4caf50; font-size:14px;">●</span>
              <span style="font-size:12px; color:#7a7d8a;">Groq Connected</span>
            </div>
            """, unsafe_allow_html=True)

            # ── New Chat ──
            st.markdown("<div style='padding:0 4px;'>", unsafe_allow_html=True)
            if st.button("＋  New Conversation", key="new_chat_btn"):
                new_conversation()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div style="padding:0 16px; margin-bottom:8px;">
              <div style="font-size:11px; color:#4a4d5a; letter-spacing:0.06em; text-transform:uppercase;">
                Conversation History
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Conversation list ──
            convs = st.session_state.conversations
            if not convs:
                st.markdown("""
                <div style="padding:16px; text-align:center; color:#4a4d5a; font-size:13px;">
                  No conversations yet.<br>Start chatting below!
                </div>
                """, unsafe_allow_html=True)
            else:
                for cid, conv in reversed(list(convs.items())):
                    is_active = cid == st.session_state.active_conv_id
                    bg = "rgba(201,168,76,0.08)" if is_active else "transparent"
                    border = "rgba(201,168,76,0.35)" if is_active else "transparent"
                    title_color = "#c9a84c" if is_active else "#a0a3b1"
                    msg_count = len(conv["messages"])

                    st.markdown(f"""
                    <div style="padding:10px 14px; margin:2px 4px; background:{bg};
                                border:1px solid {border}; border-radius:10px; cursor:pointer;
                                transition:all 0.2s;" id="conv_{cid}">
                      <div style="font-size:13px; color:{title_color}; font-weight:500;
                                  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                                  max-width:180px;">{conv['title']}</div>
                      <div style="font-size:10px; color:#4a4d5a; margin-top:2px;">
                        {conv['created_at']} · {msg_count//2} Q&A
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if st.button(f"Open", key=f"open_{cid}",
                                 help=conv["title"]):
                        st.session_state.active_conv_id = cid
                        st.rerun()

            # ── Disconnect ──
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            st.divider()
            st.markdown("<div style='padding:0 4px;'>", unsafe_allow_html=True)
            if st.button("🔌  Disconnect", key="disconnect_btn"):
                st.session_state.groq_api_key = ""
                st.session_state.api_key_valid = False
                st.session_state.active_conv_id = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Legal topics reference ──
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:0 16px;">
          <div style="font-size:10px; color:#4a4d5a; letter-spacing:0.06em;
                      text-transform:uppercase; margin-bottom:10px;">Coverage</div>
          <div style="display:flex; flex-wrap:wrap; gap:5px;">
        """, unsafe_allow_html=True)

        topics = ["BNS 2023", "BNSS 2023", "BSA 2023", "Constitution", "CPC",
                  "Contract Law", "Family Law", "Labour Law", "RERA", "RTI",
                  "IP Law", "Consumer Law"]
        badges = "".join(
            f'<span style="font-size:10px; color:#6a6d7a; background:rgba(255,255,255,0.03); '
            f'border:1px solid rgba(255,255,255,0.07); border-radius:4px; padding:3px 7px;">{t}</span>'
            for t in topics
        )
        st.markdown(f"""
        {badges}
          </div>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA – Landing / Welcome
# ══════════════════════════════════════════════════════════════════════════════
def render_welcome():
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                min-height:80vh; padding:40px 20px; text-align:center;">

      <div style="margin-bottom:20px;">
        <span style="font-size:64px; filter:drop-shadow(0 0 24px rgba(201,168,76,0.4));">⚖️</span>
      </div>

      <h1 style="font-family:'Playfair Display',serif; font-size:42px; font-weight:700;
                 background:linear-gradient(135deg,#c9a84c 0%,#e8d5a3 50%,#c9a84c 100%);
                 -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                 margin-bottom:12px; letter-spacing:0.02em;">
        LexIndia
      </h1>

      <p style="font-size:15px; color:#7a7d8a; margin-bottom:8px; letter-spacing:0.04em;">
        Your AI-powered Indian Legal Assistant
      </p>

      <p style="font-size:13px; color:#4a4d5a; max-width:480px; line-height:1.7; margin-bottom:40px;">
        Ask questions about the Indian Constitution, BNS, BNSS, BSA, civil, criminal,<br>
        family, labour, property, and all major Indian laws.
      </p>

      <div style="display:grid; grid-template-columns:repeat(2,1fr); gap:12px;
                  max-width:620px; width:100%; margin-bottom:40px;">
    """, unsafe_allow_html=True)

    sample_qs = [
        ("🔒", "What are my rights if arrested?", "BNSS Section 47–60 & Article 22"),
        ("👨‍👩‍👧", "How to file for divorce under Hindu law?", "Hindu Marriage Act"),
        ("🏠", "Tenant rights under RERA 2016", "Real Estate Act"),
        ("💼", "FIR process under new BNS laws", "BNS & BNSS procedure"),
        ("📜", "What is Article 370 post-2019?", "Constitutional amendment"),
        ("⚖️", "Bail provisions under BNSS 2023", "Bail reform changes"),
    ]

    cols = st.columns(2)
    for i, (icon, q, sub) in enumerate(sample_qs):
        with cols[i % 2]:
            if st.button(
                f"{icon}  {q}\n↳ {sub}",
                key=f"sample_{i}",
            ):
                if st.session_state.api_key_valid:
                    cid = new_conversation()
                    st.session_state.conversations[cid]["messages"].append(
                        {"role": "user", "content": q}
                    )
                    st.session_state.conversations[cid]["title"] = auto_title(q)
                    st.rerun()
                else:
                    st.warning("Please connect your Groq API key first (sidebar).")

    st.markdown("""
      </div>

      <div style="font-size:11px; color:#3a3d4a; max-width:420px; line-height:1.8; padding:16px;
                  border:1px solid rgba(255,255,255,0.04); border-radius:12px;">
        ⚠️ LexIndia provides general legal information only. For specific legal advice,
        consult a qualified advocate. This tool covers updated BNS, BNSS &amp; BSA 2023 laws.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA – Active Chat
# ══════════════════════════════════════════════════════════════════════════════
def render_chat(conv: dict, cid: str):
    messages = conv["messages"]

    # ── Chat header ──
    st.markdown(f"""
    <div style="padding:16px 32px; border-bottom:1px solid rgba(201,168,76,0.1);
                background:rgba(10,12,16,0.8); backdrop-filter:blur(8px);
                display:flex; align-items:center; gap:12px;">
      <span style="font-size:18px;">⚖️</span>
      <div>
        <div style="font-family:'Playfair Display',serif; font-size:16px; color:#c9a84c;
                    font-weight:600;">{conv['title']}</div>
        <div style="font-size:11px; color:#4a4d5a;">Started {conv['created_at']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Message history ──
    chat_container = st.container()
    with chat_container:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        for msg in messages:
            if msg["role"] == "user":
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"""
                    <div style="background:var(--user-bubble); border:1px solid rgba(201,168,76,0.1);
                                border-radius:12px 12px 4px 12px; padding:14px 18px;
                                font-size:14px; line-height:1.7; color:#d0ccc4; max-width:85%;">
                      {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                with st.chat_message("assistant", avatar="⚖️"):
                    st.markdown(f"""
                    <div style="background:var(--ai-bubble); border:1px solid rgba(201,168,76,0.08);
                                border-radius:12px 12px 12px 4px; padding:18px 22px;
                                font-size:14px; line-height:1.8; color:#ccc8c0; max-width:90%;">
                      {msg['content']}
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)

    # ── Input ──
    st.markdown("""
    <div style="position:fixed; bottom:0; left:260px; right:0; padding:16px 32px 20px;
                background:linear-gradient(to top, #0a0c10 60%, transparent);
                z-index:999;">
    """, unsafe_allow_html=True)

    if prompt := st.chat_input("Ask any legal question… (BNS, BNSS, BSA, Constitution, etc.)"):
        # Append user message
        conv["messages"].append({"role": "user", "content": prompt})

        # Auto-title on first message
        if len(conv["messages"]) == 1:
            conv["title"] = auto_title(prompt)

        with st.chat_message("user", avatar="👤"):
            st.markdown(f"""
            <div style="background:var(--user-bubble); border:1px solid rgba(201,168,76,0.1);
                        border-radius:12px 12px 4px 12px; padding:14px 18px;
                        font-size:14px; line-height:1.7; color:#d0ccc4;">
              {prompt}
            </div>
            """, unsafe_allow_html=True)

        with st.chat_message("assistant", avatar="⚖️"):
            response_placeholder = st.empty()
            full_response = ""

            with st.spinner("Consulting legal database…"):
                try:
                    for token in chat_with_groq(conv["messages"], st.session_state.groq_api_key):
                        full_response += token
                        response_placeholder.markdown(f"""
                        <div style="background:var(--ai-bubble); border:1px solid rgba(201,168,76,0.08);
                                    border-radius:12px 12px 12px 4px; padding:18px 22px;
                                    font-size:14px; line-height:1.8; color:#ccc8c0;">
                          {full_response}▌
                        </div>
                        """, unsafe_allow_html=True)

                    response_placeholder.markdown(f"""
                    <div style="background:var(--ai-bubble); border:1px solid rgba(201,168,76,0.08);
                                border-radius:12px 12px 12px 4px; padding:18px 22px;
                                font-size:14px; line-height:1.8; color:#ccc8c0;">
                      {full_response}
                    </div>
                    """, unsafe_allow_html=True)

                    conv["messages"].append({"role": "assistant", "content": full_response})

                except Exception as e:
                    err_msg = f"⚠️ Error: {str(e)}"
                    response_placeholder.error(err_msg)
                    conv["messages"].append({"role": "assistant", "content": err_msg})

        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    init_state()
    render_sidebar()

    # Main area
    with st.container():
        if not st.session_state.api_key_valid:
            render_welcome()
        else:
            active = get_active()
            if active is None:
                # Auto-create or show welcome
                render_welcome()
            else:
                render_chat(active, st.session_state.active_conv_id)


if __name__ == "__main__":
    main()
