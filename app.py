import streamlit as st # type: ignore
from agent.core import build_agent
from agent.database import get_progress_summary
from agent.pdf_export import export_progress_pdf

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="EduGuide by Kim",
    page_icon="🎓",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CSS — warm editorial aesthetic: deep ink bg, amber accents, serif display
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:        #0c0e14;
    --surface:   #13161f;
    --border:    #1e2333;
    --accent:    #f0a500;
    --accent2:   #e05c2a;
    --text:      #e8eaf0;
    --muted:     #6b7280;
    --success:   #34d399;
    --warning:   #fbbf24;
    --danger:    #f87171;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Hero */
.hero-wrap {
    text-align: center;
    padding: 2.5rem 1rem 1rem;
    position: relative;
}
.hero-badge {
    display: inline-block;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #fff;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    margin-bottom: 1rem;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 3.2rem;
    line-height: 1.1;
    color: var(--text);
    margin: 0 0 0.5rem;
}
.hero-title span {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1rem;
    color: var(--muted);
    max-width: 520px;
    margin: 0 auto 2rem;
    line-height: 1.6;
}

/* Capability pills */
.pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.pill {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    color: var(--muted);
}
.pill span { color: var(--accent); margin-right: 5px; }

/* Section label */
.section-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.6rem;
    text-align: center;
}

/* Onboarding card */
.onboard-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.5rem;
}
.onboard-card h3 {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    margin: 0 0 0.8rem;
    color: var(--accent);
}
.onboard-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 0.6rem;
    font-size: 0.88rem;
    color: var(--text);
    line-height: 1.5;
}
.step-num {
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    color: #fff;
    font-weight: 700;
    font-size: 0.75rem;
    min-width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Stat cards */
.stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; }
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 10px 12px;
    text-align: center;
}
.stat-num {
    font-family: 'DM Serif Display', serif;
    font-size: 1.8rem;
    color: var(--accent);
    line-height: 1;
}
.stat-lbl { font-size: 0.7rem; color: var(--muted); margin-top: 3px; }

/* Score bar */
.score-item { margin-bottom: 10px; }
.score-label { font-size: 0.78rem; color: var(--text); margin-bottom: 3px; }
.score-bar-bg {
    background: var(--border);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
}
.score-bar-fill { height: 6px; border-radius: 4px; transition: width 0.3s; }
.score-meta { font-size: 0.7rem; color: var(--muted); margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state defaults
# ---------------------------------------------------------------------------
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# ONBOARDING SCREEN
# ---------------------------------------------------------------------------
if not st.session_state.onboarded:
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-badge">✦ AI-Powered Learning Coach</div>
        <div class="hero-title">Meet <span>EduGuide by Kim</span></div>
        <div class="hero-sub">
            Your personal tutor that explains anything, builds custom learning
            roadmaps, finds free resources, quizzes you, and tracks your growth - all in one place.
        </div>
        <div class="pills-row">
            <div class="pill"><span></span>Concept Explainer</div>
            <div class="pill"><span></span>Roadmap Builder</div>
            <div class="pill"><span></span>Resource Finder</div>
            <div class="pill"><span></span>Adaptive Quizzes</div>
            <div class="pill"><span></span>Progress Tracker</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="onboard-card">
        <h3>How it works</h3>
        <div class="onboard-step">
            <div class="step-num">1</div>
            <div>Tell the AI what you want to learn - a skill, topic, or subject area.</div>
        </div>
        <div class="onboard-step">
            <div class="step-num">2</div>
            <div>Get a personalised roadmap, concept explanations, and handpicked free resources.</div>
        </div>
        <div class="onboard-step">
            <div class="step-num">3</div>
            <div>Test yourself with adaptive quizzes that match your skill level.</div>
        </div>
        <div class="onboard-step">
            <div class="step-num">4</div>
            <div>Track your streak, scores, and topics studied - and export your progress as a PDF.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("  Start Learning", use_container_width=True, type="primary"):
            st.session_state.onboarded = True
            with st.spinner("Initialising your AI tutor..."):
                st.session_state.agent = build_agent()
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        " Welcome to **EduGuide by Kim**! I'm your personal learning coach.\n\n"
                        "Here's what I can do for you:\n"
                        "-  **Build a learning roadmap** - *'I want to learn Python'*\n"
                        "-  **Explain any concept** - *'Explain machine learning simply'*\n"
                        "-  **Find free resources** - *'Find me free SQL courses'*\n"
                        "-  **Quiz you** - *'Quiz me on data science basics'*\n"
                        "-  **Track progress** - *'Show my learning progress'*\n\n"
                        "What would you like to learn today? "
                    ),
                }
            ]
            st.rerun()
    st.stop()

# ---------------------------------------------------------------------------
# MAIN APP (post-onboarding)
# ---------------------------------------------------------------------------

# Compact header
st.markdown("""
<div style="display:flex;align-items:center;gap:12px;padding:0.8rem 0 0.4rem;">
    <div style="font-family:'DM Serif Display',serif;font-size:1.6rem;color:var(--text);">
        🎓 EduGuide by Kim <span style="background:linear-gradient(135deg,#f0a500,#e05c2a);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">AI</span>
    </div>
    <div style="font-size:0.75rem;color:var(--muted);padding-top:4px;">
        Powered by LangChain + Groq
    </div>
</div>
""", unsafe_allow_html=True)

# Suggestion chips
st.markdown('<div class="section-label">Quick prompts</div>', unsafe_allow_html=True)
suggestions = [
    " Roadmap to learn Python",
    " Explain neural networks",
    " Free SQL resources",
    " Quiz me on data science",
    " Show my progress",
]
cols = st.columns(len(suggestions))
for i, s in enumerate(suggestions):
    if cols[i].button(s, key=f"chip_{i}", use_container_width=True):
        st.session_state["prefill"] = s

st.divider()

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
prefill = st.session_state.pop("prefill", "")
user_input = st.chat_input("Ask me anything — what do you want to learn?")
active_input = user_input or prefill

if active_input:
    # Strip emoji prefix from chip suggestions
    clean_input = active_input.split(" ", 1)[-1] if active_input[0] in "🗺🧠🔍📝📊" else active_input

    st.session_state.messages.append({"role": "user", "content": active_input})
    with st.chat_message("user"):
        st.markdown(active_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = st.session_state.agent.invoke({"input": clean_input})
                response = result.get("output", "I couldn't process that. Please try again.")
            except Exception as e:
                response = f"⚠️ Something went wrong: {str(e)}"
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------------------------------------------------------------------
# Sidebar — live dashboard
# ---------------------------------------------------------------------------
with st.sidebar:
    # Live stats
    st.markdown("###  Your Progress")
    try:
        summary = get_progress_summary()

        st.markdown(f"""
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-num">{summary['streak_days']}🔥</div>
                <div class="stat-lbl">Day Streak</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">{summary['total_topics']}</div>
                <div class="stat-lbl">Topics Studied</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">{summary['total_quizzes']}</div>
                <div class="stat-lbl">Quizzes Taken</div>
            </div>
            <div class="stat-card">
                <div class="stat-num">{summary['total_roadmaps']}</div>
                <div class="stat-lbl">Roadmaps Built</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quiz score bars
        if summary["quizzes"]:
            st.markdown("**Recent Quiz Scores**")
            for q in summary["quizzes"][:4]:
                pct = round((q["score"] / q["total"]) * 100) if q["total"] else 0
                bar_color = "#34d399" if pct >= 80 else "#fbbf24" if pct >= 60 else "#f87171"
                st.markdown(f"""
                <div class="score-item">
                    <div class="score-label">{q['topic'].title()}</div>
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
                    </div>
                    <div class="score-meta">{q['score']}/{q['total']} · {pct}% · {q['level']}</div>
                </div>
                """, unsafe_allow_html=True)

        # PDF Export
        st.divider()
        st.markdown("###  Export Progress")
        if st.button(" Download Progress PDF", use_container_width=True):
            with st.spinner("Generating your PDF report..."):
                try:
                    pdf_path = export_progress_pdf(summary)
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label=" Click to Download",
                            data=f,
                            file_name="eduguide_progress_report.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")

    except Exception:
        st.markdown("_Progress data unavailable_")

    st.divider()
    if st.button(" Clear Chat", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": " Chat cleared! What would you like to learn?"}
        ]
        st.session_state.agent = build_agent()
        st.rerun()

    if st.button(" Back to Welcome Screen", use_container_width=True):
        st.session_state.onboarded = False
        st.rerun()