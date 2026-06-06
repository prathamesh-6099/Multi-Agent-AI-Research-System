import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind · AI Research Agent",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Premium CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

/* ═══════ RESET & BASE ═══════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif;
    color: #e2ddd5;
}

.stApp {
    background: #08080c;
    background-image:
        radial-gradient(ellipse 120% 60% at 10% -20%, rgba(124,58,237,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 80% 50% at 90% 120%, rgba(59,130,246,0.07) 0%, transparent 50%),
        radial-gradient(ellipse 50% 30% at 50% 50%, rgba(236,72,153,0.04) 0%, transparent 60%);
}

/* ═══════ HIDE STREAMLIT CHROME ═══════ */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 3rem 4rem;
    padding-top: calc(50vh - 420px);
    max-width: 1280px;
}

/* ═══════ ANIMATED GRID BACKGROUND ═══════ */
.bg-grid {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(255,255,255,0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.015) 1px, transparent 1px);
    background-size: 64px 64px;
    mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 20%, transparent 70%);
    -webkit-mask-image: radial-gradient(ellipse 60% 50% at 50% 30%, black 20%, transparent 70%);
}

/* ═══════ NOISE OVERLAY ═══════ */
.noise-overlay {
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.025;
    background: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

/* ═══════ GLOW ORB ═══════ */
.glow-orb {
    position: fixed;
    width: 400px;
    height: 400px;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.12;
    pointer-events: none;
    z-index: 0;
    animation: float 18s ease-in-out infinite;
}
.glow-orb.purple {
    background: #7c3aed;
    top: -100px;
    left: 10%;
}
.glow-orb.blue {
    background: #3b82f6;
    bottom: -120px;
    right: 8%;
    animation-delay: -7s;
    animation-duration: 22s;
}
@keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(30px, -20px) scale(1.05); }
    66% { transform: translate(-20px, 15px) scale(0.95); }
}

/* ═══════ NAV BAR ═══════ */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0;
    margin-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.nav-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
}
.nav-brand-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, #7c3aed 0%, #3b82f6 50%, #06b6d4 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 16px rgba(124,58,237,0.3);
}
.nav-brand-text {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
    font-size: 1.15rem;
    color: #f0ebe3;
    letter-spacing: -0.02em;
}
.nav-brand-text span {
    background: linear-gradient(135deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.nav-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c3aed;
    background: rgba(124,58,237,0.1);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 20px;
    padding: 0.3rem 0.8rem;
}

/* ═══════ HERO ═══════ */
.hero {
    text-align: center !important;
    padding: 1.5rem 0 2rem;
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
}
.hero-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    background: rgba(124,58,237,0.08);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 100px;
    padding: 0.4rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 1.5rem;
}
.hero-chip .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #22c55e;
    animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(34,197,94,0.4); }
    50% { opacity: 0.7; box-shadow: 0 0 0 6px rgba(34,197,94,0); }
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(3rem, 7vw, 4.5rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.04em;
    color: #f5f0e8;
    margin: 0 0 1.2rem;
}
.hero h1 .gradient-text {
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 40%, #34d399 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.1rem;
    font-weight: 400;
    color: #8a8380;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.7;
    text-align: center;
}
.hero-sub strong {
    color: #b0aaa2;
    font-weight: 500;
}

/* ═══════ STAT PILLS ═══════ */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-top: 2rem;
    flex-wrap: wrap;
}
.stat-pill {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.6rem 1.2rem;
}
.stat-pill .stat-icon {
    font-size: 1rem;
}
.stat-pill .stat-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem;
    color: #706860;
    letter-spacing: 0.06em;
}
.stat-pill .stat-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    color: #d5cfc7;
}

/* ═══════ SECTION DIVIDER ═══════ */
.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(124,58,237,0.2) 20%, rgba(59,130,246,0.2) 80%, transparent 100%);
    margin: 2.5rem 0;
}

/* ═══════ SECTION LABEL ═══════ */
.section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7c3aed;
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(124,58,237,0.2), transparent);
}

/* ═══════ GLASS CARD ═══════ */
.glass-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(124,58,237,0.15);
}
.glass-card::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: 20px;
    padding: 1px;
    background: linear-gradient(135deg, rgba(124,58,237,0.1), transparent, rgba(59,130,246,0.1));
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: exclude;
    -webkit-mask-composite: xor;
    pointer-events: none;
}

/* ═══════ INPUT OVERRIDES ═══════ */
.stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-radius: 12px !important;
    color: #f0ebe0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.2rem !important;
    transition: all 0.25s ease !important;
}
.stTextInput > div > div > input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1), 0 0 30px rgba(124,58,237,0.05) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #4a4540 !important;
}
.stTextInput > label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: #a78bfa !important;
    font-weight: 500 !important;
}

/* ═══════ BUTTON ═══════ */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #6366f1 50%, #3b82f6 100%) !important;
    color: #fff !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.02em !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 24px rgba(124,58,237,0.25), 0 0 0 1px rgba(124,58,237,0.1) !important;
    width: 100%;
    position: relative;
    overflow: hidden;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(124,58,237,0.35), 0 0 0 1px rgba(124,58,237,0.2) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* ═══════ EXAMPLE CHIPS ═══════ */
.chip-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 0.8rem;
}
.chip-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #4a4540;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
.chip {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 0.35rem 0.9rem;
    font-size: 0.78rem;
    color: #908880;
    font-family: 'Inter', sans-serif;
    transition: all 0.2s ease;
    cursor: default;
}
.chip:hover {
    border-color: rgba(124,58,237,0.3);
    color: #b0a8a0;
    background: rgba(124,58,237,0.05);
}

/* ═══════ PIPELINE AGENT CARDS ═══════ */
.agent-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.8rem;
    position: relative;
    overflow: hidden;
    transition: all 0.35s ease;
}
.agent-card.running {
    border-color: rgba(124,58,237,0.35);
    background: rgba(124,58,237,0.04);
    box-shadow: 0 0 30px rgba(124,58,237,0.06);
}
.agent-card.done {
    border-color: rgba(34,197,94,0.25);
    background: rgba(34,197,94,0.03);
}

/* Left accent bar */
.agent-card::after {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    border-radius: 16px 0 0 16px;
    background: rgba(255,255,255,0.04);
    transition: background 0.35s ease;
}
.agent-card.running::after {
    background: linear-gradient(180deg, #7c3aed, #3b82f6);
    box-shadow: 0 0 12px rgba(124,58,237,0.3);
}
.agent-card.done::after {
    background: #22c55e;
}

.agent-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.agent-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}
.agent-icon.search  { background: rgba(168,85,247,0.12); }
.agent-icon.reader  { background: rgba(59,130,246,0.12); }
.agent-icon.writer  { background: rgba(236,72,153,0.12); }
.agent-icon.critic  { background: rgba(34,197,94,0.12); }

.agent-info {
    flex: 1;
    min-width: 0;
}
.agent-name {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: #e5e0d8;
    letter-spacing: -0.01em;
}
.agent-desc {
    font-size: 0.72rem;
    color: #605850;
    margin-top: 0.15rem;
}
.agent-status {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.4rem;
    flex-shrink: 0;
}
.status-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
}
.status-waiting .status-dot { background: #333; }
.status-waiting { color: #444; }
.status-running .status-dot {
    background: #a78bfa;
    animation: pulse 1.5s ease-in-out infinite;
}
.status-running { color: #a78bfa; }
.status-done .status-dot { background: #22c55e; }
.status-done { color: #22c55e; }

/* ═══════ RESULTS AREA ═══════ */
.report-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(124,58,237,0.15);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.report-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #7c3aed, #3b82f6, #06b6d4);
}

.feedback-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(34,197,94,0.15);
    border-radius: 20px;
    padding: 2.2rem 2.5rem;
    margin-top: 1rem;
    position: relative;
    overflow: hidden;
}
.feedback-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #22c55e, #06b6d4);
}

.panel-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.panel-header .panel-icon {
    font-size: 1.1rem;
}
.panel-header .panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}
.panel-title.purple { color: #a78bfa; }
.panel-title.green  { color: #22c55e; }

.result-content {
    font-size: 0.9rem;
    line-height: 1.85;
    color: #c5c0b8;
    white-space: pre-wrap;
    font-family: 'Inter', sans-serif;
}

/* ═══════ RAW OUTPUT PANEL ═══════ */
.raw-panel {
    background: rgba(255,255,255,0.015);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-top: 0.8rem;
}
.raw-panel-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #605850;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* ═══════ DOWNLOAD BUTTON ═══════ */
.stDownloadButton > button {
    background: rgba(124,58,237,0.1) !important;
    border: 1px solid rgba(124,58,237,0.2) !important;
    border-radius: 12px !important;
    color: #a78bfa !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
    padding: 0.6rem 1.5rem !important;
}
.stDownloadButton > button:hover {
    background: rgba(124,58,237,0.15) !important;
    border-color: rgba(124,58,237,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ═══════ SPINNER ═══════ */
.stSpinner > div { color: #a78bfa !important; }

/* ═══════ EXPANDER ═══════ */
details summary {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    color: #706860 !important;
    letter-spacing: 0.08em !important;
    cursor: pointer;
    transition: color 0.2s ease;
}
details summary:hover {
    color: #a78bfa !important;
}
details[open] summary {
    color: #a78bfa !important;
}

/* ═══════ FOOTER ═══════ */
.footer {
    text-align: center;
    margin-top: 4rem;
    padding: 1.5rem 0;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.footer-text {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem;
    color: #3a3530;
    letter-spacing: 0.1em;
}
.footer-text span {
    color: #7c3aed;
}

/* ═══════ SCROLLBAR ═══════ */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124,58,237,0.35); }

/* ═══════ ANIMATION ═══════ */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeInUp 0.5s ease-out forwards;
}

/* ═══════ PROGRESS BAR ═══════ */
.progress-track {
    height: 3px;
    background: rgba(255,255,255,0.04);
    border-radius: 4px;
    margin: 1.2rem 0 0.6rem;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, #7c3aed, #3b82f6, #06b6d4);
    transition: width 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}
.progress-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem;
    color: #504840;
    letter-spacing: 0.08em;
}

/* ═══════ TOAST / WARNING ═══════ */
.stAlert > div {
    background: rgba(234,179,8,0.06) !important;
    border: 1px solid rgba(234,179,8,0.15) !important;
    border-radius: 12px !important;
    color: #d4a920 !important;
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)


# ── Background layers ────────────────────────────────────────────────────────
st.markdown("""
<div class="bg-grid"></div>
<div class="noise-overlay"></div>
<div class="glow-orb purple"></div>
<div class="glow-orb blue"></div>
""", unsafe_allow_html=True)


# ── Helper: agent pipeline card ───────────────────────────────────────────────
def agent_card(icon: str, icon_cls: str, name: str, desc: str, state: str):
    status_map = {
        "waiting": ("Queued", "status-waiting"),
        "running": ("Running", "status-running"),
        "done":    ("Complete", "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    card_cls = {"running": "running", "done": "done"}.get(state, "")
    st.markdown(f"""
    <div class="agent-card {card_cls}">
        <div class="agent-header">
            <div class="agent-icon {icon_cls}">{icon}</div>
            <div class="agent-info">
                <div class="agent-name">{name}</div>
                <div class="agent-desc">{desc}</div>
            </div>
            <div class="agent-status {cls}">
                <div class="status-dot"></div>
                {label}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


import os

# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done", "google_api_key", "tavily_api_key"):
    if key not in st.session_state:
        if key == "results":
            st.session_state[key] = {}
        elif key in ("google_api_key", "tavily_api_key"):
            st.session_state[key] = ""
        else:
            st.session_state[key] = False

# Helper: check keys configured
def check_keys_configured():
    has_google = bool(st.session_state.get("google_api_key") or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if not has_google:
        try:
            has_google = bool(st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY"))
        except Exception:
            pass
            
    has_tavily = bool(st.session_state.get("tavily_api_key") or os.getenv("TAVILY_API_KEY"))
    if not has_tavily:
        try:
            has_tavily = bool(st.secrets.get("TAVILY_API_KEY"))
        except Exception:
            pass
            
    return has_google, has_tavily

# ── Sidebar Settings ────────────────────────────────────────────────────────
has_g, has_t = check_keys_configured()

with st.sidebar:
    st.markdown('<div class="section-label">API Configuration</div>', unsafe_allow_html=True)
    
    st.markdown("<h3 style='font-size: 0.95rem; color: #a78bfa; margin-bottom: 0.4rem;'>Gemini API Key</h3>", unsafe_allow_html=True)
    google_key_input = st.text_input(
        "Gemini API Key",
        type="password",
        placeholder="Enter Gemini API Key..." if not has_g else "✓ Configured (from secrets/env)",
        key="google_key_widget",
        label_visibility="collapsed"
    )
    if google_key_input:
        st.session_state["google_api_key"] = google_key_input
        
    st.markdown("<h3 style='font-size: 0.95rem; color: #a78bfa; margin-top: 1.2rem; margin-bottom: 0.4rem;'>Tavily API Key</h3>", unsafe_allow_html=True)
    tavily_key_input = st.text_input(
        "Tavily API Key",
        type="password",
        placeholder="Enter Tavily API Key..." if not has_t else "✓ Configured (from secrets/env)",
        key="tavily_key_widget",
        label_visibility="collapsed"
    )
    if tavily_key_input:
        st.session_state["tavily_api_key"] = tavily_key_input

    st.markdown("""
    <div style="font-size: 0.8rem; color: #706860; line-height: 1.5; margin-top: 2rem;">
    💡 <strong>Note:</strong> API keys entered here are temporary and only stored in your current session.
    <br><br>
    To make them permanent on Streamlit Cloud, add them to your app secrets:
    <pre style="background: #111; color: #a78bfa; padding: 0.5rem; border-radius: 4px; font-size: 0.75rem; overflow-x: auto; margin-top: 0.5rem;">
GOOGLE_API_KEY = "your-gemini-key"
TAVILY_API_KEY = "your-tavily-key"
    </pre>
    </div>
    """, unsafe_allow_html=True)


# ── Nav Bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
    <div class="nav-brand">
        <div class="nav-brand-icon">🧠</div>
        <div class="nav-brand-text">Research<span>Mind</span></div>
    </div>
    <div class="nav-badge">Multi-Agent System</div>
</div>
""", unsafe_allow_html=True)


# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero animate-in">
    <div class="hero-chip">
        <span class="dot"></span>
        4 AI Agents · Collaborative Pipeline
    </div>
    <h1>Research with<br><span class="gradient-text">Intelligent Agents</span></h1>
    <p class="hero-sub">
        Four specialized AI agents work in concert — <strong>searching</strong>,
        <strong>scraping</strong>, <strong>writing</strong>, and <strong>critiquing</strong>
        — to deliver polished, in-depth research reports on any topic.
    </p>
    <div class="stat-row">
        <div class="stat-pill">
            <span class="stat-icon">🔍</span>
            <div>
                <div class="stat-label">Agent 1</div>
                <div class="stat-value">Web Search</div>
            </div>
        </div>
        <div class="stat-pill">
            <span class="stat-icon">📄</span>
            <div>
                <div class="stat-label">Agent 2</div>
                <div class="stat-value">Content Reader</div>
            </div>
        </div>
        <div class="stat-pill">
            <span class="stat-icon">✍️</span>
            <div>
                <div class="stat-label">Chain 1</div>
                <div class="stat-value">Report Writer</div>
            </div>
        </div>
        <div class="stat-pill">
            <span class="stat-icon">🧐</span>
            <div>
                <div class="stat-label">Chain 2</div>
                <div class="stat-value">Quality Critic</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Section Divider ──────────────────────────────────────────────────────────
st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)


# ── Layout: Input + Pipeline ─────────────────────────────────────────────────
col_input, col_gap, col_pipeline = st.columns([5, 0.5, 4.5])

with col_input:
    st.markdown('<div class="section-label">Research Input</div>', unsafe_allow_html=True)
    
    # Re-verify configuration for UI state
    has_g, has_t = check_keys_configured()
    if not (has_g and has_t):
        st.info("💡 **Setup Required:** Please expand the sidebar on the left to enter your Gemini and Tavily API keys.")
        
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    topic = st.text_input(
        "Enter Your Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="visible",
    )
    run_btn = st.button("⚡  Launch Research Pipeline", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Example chips
    st.markdown("""
    <div class="chip-row">
        <span class="chip-label">Try →</span>
        <span class="chip">LLM agents 2025</span>
        <span class="chip">CRISPR gene editing</span>
        <span class="chip">Fusion energy progress</span>
        <span class="chip">AGI safety research</span>
    </div>
    """, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-label">Agent Pipeline</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def get_state(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        if step in r:
            return "done"
        if st.session_state.running:
            for k in steps:
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    agent_card("🔍", "search", "Search Agent",   "Web search for latest information",   get_state("search"))
    agent_card("📄", "reader", "Reader Agent",    "Deep scrape & content extraction",    get_state("reader"))
    agent_card("✍️", "writer", "Writer Chain",    "Draft comprehensive research report",  get_state("writer"))
    agent_card("🧐", "critic", "Critic Chain",    "Quality review & scoring",             get_state("critic"))

    # Progress bar
    completed = sum(1 for k in ["search", "reader", "writer", "critic"] if k in r)
    pct = int(completed / 4 * 100)
    st.markdown(f"""
    <div class="progress-track">
        <div class="progress-fill" style="width:{pct}%"></div>
    </div>
    <div class="progress-label">{completed}/4 stages complete · {pct}%</div>
    """, unsafe_allow_html=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    has_g, has_t = check_keys_configured()
    if not topic.strip():
        st.warning("⚠ Please enter a research topic to begin.")
    elif not (has_g and has_t):
        st.error("⚠ Missing API keys. Please configure both Gemini and Tavily API keys in the sidebar.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    try:
        # ── Step 1: Search ──
        with st.spinner("🔍  Search Agent is gathering information…"):
            search_agent = build_search_agent()
            sr = search_agent.invoke({
                "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
            })
            results["search"] = sr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 2: Reader ──
        with st.spinner("📄  Reader Agent is scraping top resources…"):
            reader_agent = build_reader_agent()
            rr = reader_agent.invoke({
                "messages": [("user",
                    f"Based on the following search results about '{topic_val}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{results['search'][:800]}"
                )]
            })
            results["reader"] = rr["messages"][-1].content
            st.session_state.results = dict(results)

        # ── Step 3: Writer ──
        with st.spinner("✍️  Writer is drafting the research report…"):
            research_combined = (
                f"SEARCH RESULTS:\n{results['search']}\n\n"
                f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
            )
            results["writer"] = writer_chain.invoke({
                "topic": topic_val,
                "research": research_combined
            })
            st.session_state.results = dict(results)

        # ── Step 4: Critic ──
        with st.spinner("🧐  Critic is reviewing the report…"):
            results["critic"] = critic_chain.invoke({
                "report": results["writer"]
            })
            st.session_state.results = dict(results)

        st.session_state.running = False
        st.session_state.done = True
        st.rerun()

    except Exception as e:
        st.session_state.running = False
        st.session_state.done = False
        clean_error = str(e).replace("[type=", " (type=").replace("]", ")")
        st.error(f"❌ **An error occurred during pipeline execution:** {clean_error}")


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Research Results</div>', unsafe_allow_html=True)

    # Raw outputs in expanders
    if "search" in r:
        with st.expander("🔍  Search Agent — Raw Output", expanded=False):
            st.markdown(f"""
            <div class="raw-panel">
                <div class="raw-panel-title">Search Agent Response</div>
                <div class="result-content">{r["search"]}</div>
            </div>
            """, unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("📄  Reader Agent — Scraped Content", expanded=False):
            st.markdown(f"""
            <div class="raw-panel">
                <div class="raw-panel-title">Reader Agent Response</div>
                <div class="result-content">{r["reader"]}</div>
            </div>
            """, unsafe_allow_html=True)

    # Final report
    if "writer" in r:
        st.markdown("""
        <div class="report-card">
            <div class="panel-header">
                <span class="panel-icon">📝</span>
                <span class="panel-title purple">Final Research Report</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Download
        st.download_button(
            label="⬇  Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    # Critic feedback
    if "critic" in r:
        st.markdown("""
        <div class="feedback-card">
            <div class="panel-header">
                <span class="panel-icon">🧐</span>
                <span class="panel-title green">Critic Feedback & Score</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    <div class="footer-text">
        <span>ResearchMind</span> · Powered by LangChain Multi-Agent Pipeline · Built with Streamlit · 2025
    </div>
</div>
""", unsafe_allow_html=True)