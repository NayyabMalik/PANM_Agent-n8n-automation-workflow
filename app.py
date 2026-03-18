import streamlit as st
import requests
import psycopg2
import psycopg2.extras
import json
import time
import hashlib
from datetime import datetime
import uuid

st.set_page_config(
    page_title="PANM Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg:        #07090f;
    --surface:   #0c0f1a;
    --card:      #111520;
    --border:    #1a1f2e;
    --border2:   #1e2840;
    --accent:    #6366f1;
    --accent2:   #818cf8;
    --glow:      rgba(99,102,241,0.18);
    --green:     #22c55e;
    --amber:     #f59e0b;
    --red:       #ef4444;
    --text:      #e8eaf0;
    --text-dim:  #4a5568;
    --text-mid:  #8892a4;
    --user-bg:   #0f1320;
    --agent-bg:  #080e1e;
    --radius:    12px;
}

html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: var(--bg) !important;
    font-family: 'Outfit', sans-serif;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] > div { padding-top: 0; }
footer { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }

::-webkit-scrollbar { width: 3px; height: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }

/* ── Sidebar brand header ── */
.brand-block {
    background: linear-gradient(135deg, #0f1535 0%, #1a1040 100%);
    border-bottom: 1px solid var(--border2);
    padding: 1.4rem 1.2rem 1.1rem;
    margin-bottom: 0.9rem;
}
.brand-icon {
    font-size: 1.8rem;
    margin-bottom: 0.3rem;
    display: block;
}
.brand-name {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: -0.01em;
    color: var(--text);
    line-height: 1.1;
}
.brand-name span {
    background: linear-gradient(90deg, #818cf8, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.brand-tagline {
    font-size: 0.65rem;
    font-family: 'DM Mono', monospace;
    color: var(--text-dim);
    margin-top: 4px;
    letter-spacing: 0.04em;
}
.brand-by {
    font-size: 0.62rem;
    font-family: 'DM Mono', monospace;
    color: #6366f144;
    margin-top: 2px;
}

/* ── Status pills ── */
.status-row {
    display: flex; align-items: center; gap: 7px;
    padding: 5px 9px; background: var(--card);
    border: 1px solid var(--border); border-radius: 7px;
    margin-bottom: 4px; font-size: 0.72rem;
    font-family: 'DM Mono', monospace; color: var(--text-mid);
}
.dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.dot-green { background: var(--green); box-shadow: 0 0 6px var(--green); }
.dot-blue  { background: var(--accent2); box-shadow: 0 0 6px var(--accent2); }
.dot-red   { background: var(--red); box-shadow: 0 0 6px var(--red); }
.dot-amber { background: var(--amber); box-shadow: 0 0 6px var(--amber); }

/* ── Section labels ── */
.section-label {
    font-size: 0.6rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.14em; color: var(--text-dim); margin: 1rem 0 0.4rem;
    padding: 0 0.1rem;
}

/* ── Sidebar buttons ── */
.stButton > button {
    background: var(--card) !important; color: var(--text-mid) !important;
    border: 1px solid var(--border) !important; border-radius: 7px !important;
    font-family: 'Outfit', sans-serif !important; font-size: 0.77rem !important;
    font-weight: 500 !important; padding: 0.35rem 0.8rem !important;
    text-align: left !important; transition: all 0.12s !important;
    width: 100% !important; margin-bottom: 2px !important;
}
.stButton > button:hover {
    background: var(--border) !important;
    border-color: var(--border2) !important; color: var(--text) !important;
}

/* ── Send button ── */
.send-btn > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: white !important; border: none !important;
    font-size: 0.84rem !important; font-weight: 700 !important;
    border-radius: 9px !important; padding: 0.48rem 1.3rem !important;
    letter-spacing: 0.02em !important; width: auto !important;
}
.send-btn > button:hover {
    background: linear-gradient(135deg, #818cf8, #6366f1) !important;
    box-shadow: 0 0 22px var(--glow) !important;
    transform: translateY(-1px) !important;
}

/* ── Stat cards ── */
.stat-card {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 9px; padding: 0.6rem 0.3rem; text-align: center;
}
.stat-val { font-size: 1.3rem; font-weight: 800; color: var(--accent2); line-height: 1; }
.stat-lbl {
    font-size: 0.58rem; font-family: 'DM Mono', monospace;
    color: var(--text-dim); margin-top: 2px;
    text-transform: uppercase; letter-spacing: 0.08em;
}

/* ── Main page header ── */
.page-header {
    padding: 1.4rem 0 0.2rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 1.1rem;
}
.page-logo-row {
    display: flex; align-items: center; gap: 12px; margin-bottom: 4px;
}
.page-logo-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border: 1px solid #4338ca44;
    border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
}
.page-title-text {
    font-size: 1.5rem; font-weight: 900;
    letter-spacing: -0.03em; color: var(--text); line-height: 1;
}
.page-title-text span {
    background: linear-gradient(90deg, #818cf8 0%, #a78bfa 60%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.page-title-sub {
    font-size: 0.7rem; font-family: 'DM Mono', monospace;
    color: var(--text-dim); margin-top: 2px;
}
.page-desc {
    font-size: 0.75rem; color: var(--text-dim);
    font-family: 'DM Mono', monospace; margin-top: 0.5rem;
}

/* ── Tool badges ── */
.badges { display: flex; flex-wrap: wrap; gap: 5px; margin: 0.7rem 0 0; }
.badge {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 9px; border-radius: 20px;
    font-size: 0.65rem; font-family: 'DM Mono', monospace;
    font-weight: 500; border: 1px solid;
}
.b-web   { background:#0f1f3d; color:#60a5fa; border-color:#1d4ed833; }
.b-gmail { background:#1f0f0f; color:#f87171; border-color:#b91c1c33; }
.b-cal   { background:#0f1f14; color:#4ade80; border-color:#15803d33; }
.b-doc   { background:#0f1520; color:#818cf8; border-color:#4338ca33; }
.b-sheet { background:#0f1f14; color:#34d399; border-color:#05966933; }
.b-scrape{ background:#1a0f26; color:#c084fc; border-color:#7e22ce33; }
.b-exp   { background:#1f1a0f; color:#fbbf24; border-color:#b4570833; }

/* ── Chat bubbles ── */
.chat-wrap { display: flex; flex-direction: column; gap: 20px; margin-bottom: 1.8rem; }
.msg-row-user  { display: flex; justify-content: flex-end; }
.msg-row-agent { display: flex; justify-content: flex-start; }
.bubble {
    max-width: 74%; padding: 0.78rem 1rem;
    border-radius: var(--radius); font-size: 0.875rem;
    line-height: 1.65; word-break: break-word;
    font-family: 'Outfit', sans-serif;
}
.bubble-user {
    background: var(--user-bg);
    border: 1px solid var(--border2);
    border-bottom-right-radius: 3px;
}
.bubble-agent {
    background: var(--agent-bg);
    border: 1px solid #252f50;
    border-bottom-left-radius: 3px;
    position: relative;
}
.bubble-agent::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, #6366f133, transparent);
    border-radius: var(--radius) var(--radius) 0 0;
}
.bubble-meta {
    font-size: 0.59rem; font-family: 'DM Mono', monospace;
    color: var(--text-dim); margin-bottom: 6px;
    display: flex; align-items: center; gap: 5px;
}
.bubble-meta-user::before { content: '👤'; font-size: 0.65rem; }
.bubble-meta-agent::before { content: '🧠'; font-size: 0.65rem; }
.bubble-meta-agent { color: #6366f166; }

/* ── Input area ── */
.stTextArea {
    background: var(--card) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--radius) !important;
    padding: 0.7rem 0.85rem 0.55rem !important;
    margin-top: 1.4rem !important;
}
.stTextArea textarea {
    background: transparent !important; border: none !important;
    border-bottom: 1px solid var(--border) !important;
    border-radius: 0 !important; color: var(--text) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.88rem !important; padding: 0.3rem 0 !important;
    resize: none !important; box-shadow: none !important;
}
.stTextArea textarea:focus {
    border-bottom-color: var(--accent) !important; box-shadow: none !important;
}
.stTextArea label { display: none !important; }

/* ── Agent thinking/stream box ── */
.think-box {
    background: #06091a; border: 1px solid #1e2545;
    border-left: 2px solid var(--accent); border-radius: 10px;
    padding: 0.75rem 1rem; font-family: 'DM Mono', monospace;
    font-size: 0.77rem; color: #818cf8; line-height: 1.75;
    white-space: pre-wrap; word-break: break-word; margin: 6px 0 10px;
}
.err-box {
    background: #140a0a; border: 1px solid #7f1d1d44;
    border-left: 2px solid var(--red); border-radius: 10px;
    padding: 0.75rem 1rem; font-family: 'DM Mono', monospace;
    font-size: 0.77rem; color: #fca5a5; white-space: pre-wrap;
}
.warn-box {
    background: #140f07; border: 1px solid #78350f44;
    border-left: 2px solid var(--amber); border-radius: 10px;
    padding: 0.75rem 1rem; font-family: 'DM Mono', monospace;
    font-size: 0.77rem; color: #fcd34d; white-space: pre-wrap;
}
.think-label {
    font-size: 0.6rem; font-family: 'DM Mono', monospace;
    color: var(--text-dim); text-transform: uppercase;
    letter-spacing: 0.12em; margin-bottom: 3px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important; gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--text-dim) !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.8rem !important; font-weight: 600 !important;
    padding: 0.42rem 1rem !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important; border-bottom-color: var(--accent) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1rem !important; }
hr { border-color: var(--border) !important; margin: 0.6rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ─── Config ───────────────────────────────────────────────────────────────────
N8N_WEBHOOK_PROD = "http://localhost:5678/webhook/b19536a2-4d87-4b1c-b6fe-da596320aa22"

DB_BASE = {
    "database": "memory_db",
    "user": "postgres",
    "password": "postgres",
    "port": 5442,
    "sslmode": "disable",
    "connect_timeout": 4,
}
DB_HOSTS = ["localhost", "127.0.0.1", "host.docker.internal", "192.168.10.8"]

# ─── Secure session ───────────────────────────────────────────────────────────
def make_session_id() -> str:
    return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:20]

def mask_session(sid: str) -> str:
    return sid[:4] + " •••• " + sid[-2:]

# ─── DB ───────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def detect_db_host():
    results = []
    for host in DB_HOSTS:
        try:
            conn = psycopg2.connect(**{**DB_BASE, "host": host})
            conn.close()
            return host, None
        except Exception as e:
            results.append(f"{host} → {str(e)[:55]}")
    return None, "No host worked:\n" + "\n".join(results)

def get_conn():
    host, err = detect_db_host()
    if not host:
        raise Exception(err)
    return psycopg2.connect(**{**DB_BASE, "host": host})

def init_db():
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS conversation_logs (
                id SERIAL PRIMARY KEY, session_id TEXT NOT NULL,
                role TEXT NOT NULL, message TEXT NOT NULL,
                tool_used TEXT, created_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit(); cur.close(); conn.close()
    except Exception:
        pass

def save_message(sid, role, msg, tool=None):
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute(
            "INSERT INTO conversation_logs (session_id,role,message,tool_used) VALUES (%s,%s,%s,%s)",
            (sid, role, msg, tool)
        )
        conn.commit(); cur.close(); conn.close()
    except Exception:
        pass

def load_history(sid):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM conversation_logs WHERE session_id=%s ORDER BY created_at", (sid,))
        rows = cur.fetchall(); cur.close(); conn.close()
        return list(rows)
    except Exception:
        return []

def load_all_sessions():
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT session_id, COUNT(*) as msg_count, MAX(created_at) as last_active
            FROM conversation_logs GROUP BY session_id ORDER BY last_active DESC LIMIT 20
        """)
        rows = cur.fetchall(); cur.close(); conn.close()
        return list(rows)
    except Exception:
        return []

def get_stats():
    try:
        conn = get_conn(); cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM conversation_logs"); total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT session_id) FROM conversation_logs"); sess = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM conversation_logs WHERE role='assistant'"); rep = cur.fetchone()[0]
        cur.close(); conn.close()
        return total, sess, rep
    except Exception:
        return 0, 0, 0

# ─── n8n ──────────────────────────────────────────────────────────────────────
def extract_n8n_result(data) -> str:
    if isinstance(data, list):
        if not data: return "(empty response)"
        item = data[0]
        if isinstance(item, dict):
            return (item.get("output") or item.get("text") or
                    item.get("message") or item.get("response") or json.dumps(item, indent=2))
        return str(item)
    if isinstance(data, dict):
        return (data.get("output") or data.get("text") or
                data.get("message") or data.get("response") or json.dumps(data, indent=2))
    return str(data)

def stream_text(text: str, placeholder):
    words = text.split()
    displayed = ""
    for i, word in enumerate(words):
        displayed += word + " "
        if i % 4 == 0:
            placeholder.markdown(
                f'<div class="think-box">{displayed}▌</div>',
                unsafe_allow_html=True
            )
            time.sleep(0.022)
    placeholder.markdown(
        f'<div class="msg-row-agent"><div class="bubble bubble-agent">'
        f'<div class="bubble-meta bubble-meta-agent">PANM Agent</div>'
        f'{displayed.strip()}</div></div>',
        unsafe_allow_html=True
    )

def call_n8n(message: str, stream_ph, sid: str):
    payload = {"message": message, "session_id": sid}
    stream_ph.markdown('<div class="think-box">🧠 PANM Agent is thinking…▌</div>', unsafe_allow_html=True)
    try:
        resp = requests.post(N8N_WEBHOOK_PROD, json=payload, timeout=120)

        if resp.status_code == 500:
            try:
                ed = resp.json()
                emsg = ed.get("message") or ed.get("error") or json.dumps(ed)
            except Exception:
                emsg = resp.text or "No detail"
            result = (
                f"⚠️  n8n workflow error (HTTP 500)\n\n"
                f"Detail: {emsg}\n\n"
                f"Checklist:\n"
                f"  • n8n Executions tab → find the red node\n"
                f"  • Verify credentials (Google OAuth, OpenRouter, Postgres)\n"
                f"  • AI Agent node needs a model selected\n"
                f"  • Postgres Chat Memory DB settings must match"
            )
            stream_ph.markdown(f'<div class="warn-box">{result}</div>', unsafe_allow_html=True)
            return result

        resp.raise_for_status()
        try:
            result = extract_n8n_result(resp.json())
        except Exception:
            result = resp.text or "(no response body)"

        stream_text(result, stream_ph)
        return result

    except requests.exceptions.ConnectionError:
        err = "❌  Cannot connect to n8n at localhost:5678\nIs n8n running?"
        stream_ph.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        return err
    except requests.exceptions.Timeout:
        err = "⏱  Timed out (120s).\nCheck n8n Executions — agent may still be running."
        stream_ph.markdown(f'<div class="warn-box">{err}</div>', unsafe_allow_html=True)
        return err
    except Exception as e:
        err = f"❌  Error:\n{str(e)}"
        stream_ph.markdown(f'<div class="err-box">{err}</div>', unsafe_allow_html=True)
        return err

# ─── State ────────────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = make_session_id()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
init_db()

# ═══════════════════════ SIDEBAR ══════════════════════════════════════════════
with st.sidebar:

    # Brand block at top
    st.markdown("""
    <div class="brand-block">
      <span class="brand-icon">🧠</span>
      <div class="brand-name">PANM <span>Agent</span></div>
      <div class="brand-tagline">Personal Assistant · AI Powered</div>
      <div class="brand-by">by Nayyab Malik</div>
    </div>
    """, unsafe_allow_html=True)

    # Status indicators
    db_host, db_err = detect_db_host()
    if db_host:
        st.markdown(
            f'<div class="status-row"><span class="dot dot-green"></span>'
            f'PostgreSQL &nbsp;<code style="color:#22c55e;font-size:0.68rem">{db_host}:5442</code></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-row"><span class="dot dot-red"></span>'
            '<span style="color:#ef4444">PostgreSQL unreachable</span></div>',
            unsafe_allow_html=True
        )
        with st.expander("Diagnostics"):
            st.code(db_err or "Unknown", language=None)

    st.markdown(
        '<div class="status-row"><span class="dot dot-blue"></span>'
        'n8n &nbsp;<code style="color:#818cf8;font-size:0.68rem">localhost:5678 · live</code></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="status-row"><span class="dot dot-amber"></span>'
        f'<span style="font-size:0.68rem">Session &nbsp;</span>'
        f'<code style="color:#fbbf24;font-size:0.65rem">{mask_session(st.session_state.session_id)}</code></div>',
        unsafe_allow_html=True
    )

    # Session controls
    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("＋ New", key="new_sess"):
            st.session_state.session_id = make_session_id()
            st.session_state.chat_history = []
            st.rerun()
    with c2:
        if st.button("🗑 Clear", key="clr_chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Quick tasks
    st.markdown('<div class="section-label">Quick Tasks</div>', unsafe_allow_html=True)
    quick_tasks = {
        "🔍 Web Search → Sheet":  "Search the web for a company that sells solar panels. Extract company name and website. Save to Google Sheet named 'Leads'.",
        "📧 Gmail Summary":        "Get my latest 5 messages from Gmail and summarise each one.",
        "📅 This Week's Events":   "Get all my Google Calendar events for this week.",
        "💰 Log Expense":          "Add an expense: Category: Research, Description: Lead finding, Amount: 20, Date: today.",
        "🌐 Scrape → Doc":         "Scrape the homepage of anthropic.com and store a summary in a Google Document.",
        "🧪 Full Pipeline Test":   "Test all tools:\n1. Search web for solar panel company\n2. Save name + URL to 'Leads' sheet\n3. Create summary Google Doc\n4. Log expense: Research / Lead finding / $20 / today",
    }
    for label, prompt in quick_tasks.items():
        if st.button(label, key=f"qt_{label}"):
            st.session_state["prefill"] = prompt
            st.rerun()

    # Stats
    st.markdown('<div class="section-label">Stats</div>', unsafe_allow_html=True)
    total, sessions, replies = get_stats()
    s1, s2, s3 = st.columns(3)
    for col, val, lbl in [(s1, total, "msgs"), (s2, sessions, "sess"), (s3, replies, "replies")]:
        with col:
            st.markdown(
                f'<div class="stat-card"><div class="stat-val">{val}</div>'
                f'<div class="stat-lbl">{lbl}</div></div>',
                unsafe_allow_html=True
            )

# ═══════════════════════ MAIN ═════════════════════════════════════════════════
st.markdown("""
<div class="page-header">
  <div class="page-logo-row">
    <div class="page-logo-icon">🧠</div>
    <div>
      <div class="page-title-text">PANM <span>Agent</span></div>
      <div class="page-title-sub">Personal Assistant by Nayyab Malik</div>
    </div>
  </div>
  <div class="page-desc">Powered by n8n</div>

</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬  Chat", "📜  History", "🗄️  DB Logs"])

# ─── CHAT ─────────────────────────────────────────────────────────────────────
with tab1:
    if st.session_state.chat_history:
        st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
        for turn in st.session_state.chat_history:
            t = turn.get("time", "")
            if turn["role"] == "user":
                st.markdown(f"""
                <div class="msg-row-user">
                  <div class="bubble bubble-user">
                    <div class="bubble-meta bubble-meta-user">You · {t}</div>
                    {turn["content"]}
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="msg-row-agent">
                  <div class="bubble bubble-agent">
                    <div class="bubble-meta bubble-meta-agent">PANM Agent · {t}</div>
                    {turn["content"]}
                  </div>
                </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    prefill = st.session_state.pop("prefill", "")
    user_input = st.text_area(
        "msg",
        value=prefill,
        placeholder="Ask PANM Agent anything — search, email, calendar, docs, sheets, expenses…",
        height=85,
        label_visibility="collapsed",
        key="chat_input"
    )

    ca, cb = st.columns([2, 8])
    with ca:
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        send = st.button("Send  ➤", key="send_btn")
        st.markdown('</div>', unsafe_allow_html=True)
    with cb:
        st.markdown(
            '<span style="font-size:0.68rem;color:#2a3040;font-family:DM Mono,monospace">'
            'Try Quick Tasks in the sidebar ← for one-click prompts</span>',
            unsafe_allow_html=True
        )

    if send and user_input.strip():
        now = datetime.now().strftime("%H:%M")
        st.session_state.chat_history.append({"role": "user", "content": user_input.strip(), "time": now})
        save_message(st.session_state.session_id, "user", user_input.strip())

        st.markdown('<div class="think-label">🧠 PANM Agent is working…</div>', unsafe_allow_html=True)
        stream_ph = st.empty()
        stream_ph.markdown('<div class="think-box">▌</div>', unsafe_allow_html=True)

        result = call_n8n(user_input.strip(), stream_ph, st.session_state.session_id)
        save_message(st.session_state.session_id, "assistant", result)

        st.session_state.chat_history.append({
            "role": "assistant", "content": result,
            "time": datetime.now().strftime("%H:%M")
        })
        st.rerun()

# ─── HISTORY ──────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("#### Conversation History")
    sessions_data = load_all_sessions()
    if sessions_data:
        for s in sessions_data:
            masked = mask_session(s['session_id'])
            last   = str(s['last_active'])[:16]
            with st.expander(f"Session {masked}  ·  {s['msg_count']} messages  ·  {last}"):
                for m in load_history(s['session_id']):
                    is_user  = m['role'] == 'user'
                    row_cls  = "msg-row-user"  if is_user else "msg-row-agent"
                    bub_cls  = "bubble-user"   if is_user else "bubble-agent"
                    meta_cls = "bubble-meta bubble-meta-user" if is_user else "bubble-meta bubble-meta-agent"
                    who      = "You"           if is_user else "🧠 PANM Agent"
                    ts       = str(m['created_at'])[:16]
                    st.markdown(f"""
                    <div class="{row_cls}" style="margin-bottom:10px">
                      <div class="bubble {bub_cls}">
                        <div class="{meta_cls}">{who} · {ts}</div>
                        {m['message']}
                      </div>
                    </div>""", unsafe_allow_html=True)
    else:
        st.info("No conversations yet. Start chatting!")

# ─── DB LOGS ──────────────────────────────────────────────────────────────────
with tab3:
    st.markdown("#### Database Logs")
    st.caption("Last 50 rows from `conversation_logs` · Session IDs masked for security")
    if st.button("↻ Refresh", key="refresh_db"):
        st.rerun()
    try:
        conn = get_conn()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT id,
                   LEFT(session_id,4)||'••••'||RIGHT(session_id,2) AS session_id,
                   role, LEFT(message,100) AS message_preview,
                   tool_used, created_at
            FROM conversation_logs ORDER BY created_at DESC LIMIT 50
        """)
        rows = cur.fetchall(); cur.close(); conn.close()
        if rows:
            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True,
                column_config={
                    "id":              st.column_config.NumberColumn("ID",      width="small"),
                    "session_id":      st.column_config.TextColumn("Session",   width="small"),
                    "role":            st.column_config.TextColumn("Role",      width="small"),
                    "message_preview": st.column_config.TextColumn("Message",   width="large"),
                    "tool_used":       st.column_config.TextColumn("Tool",      width="small"),
                    "created_at":      st.column_config.DatetimeColumn("Time",  width="medium"),
                })
        else:
            st.info("No logs yet.")
    except Exception as e:
        st.error(f"DB error: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown(
    f'<p style="text-align:center;color:#1a2030;font-family:DM Mono,monospace;'
    f'font-size:0.62rem;margin-top:2rem;letter-spacing:0.05em">'
    f'PANM Agent · Personal Assistant by Nayyab Malik · {datetime.now().year}</p>',
    unsafe_allow_html=True
)