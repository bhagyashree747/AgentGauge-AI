import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benchmark.controller import run_benchmark


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AgentGauge AI | Benchmark Studio",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)
DEMO_FILE = RESULTS_DIR / "benchmark_mock_demo.json"

TASK = """
Write a Python function called is_palindrome(text).

Requirements:
- Ignore spaces and capitalization.
- Return True if the text is a palindrome.
- Return False otherwise.
- Handle empty strings and single-character strings.
"""

TEST_CODE = """
assert is_palindrome("Race car") is True
assert is_palindrome("hello") is False
assert is_palindrome("Madam") is True
assert is_palindrome("A man a plan a canal Panama") is True
assert is_palindrome("") is True
assert is_palindrome("a") is True
assert is_palindrome("Python") is False

print("ALL TESTS PASSED")
"""

# Design system
BG = "#0B1220"
PANEL = "#111C2E"
PANEL_ALT = "#152238"
BORDER = "#26364D"
TEXT = "#EDF2FA"
MUTED = "#91A1B8"
BLUE = "#78A6FF"
VIOLET = "#A78BFA"
GREEN = "#4DD4A2"
RED = "#FF7185"
AMBER = "#F6C66A"


# ============================================================
# GLOBAL STYLING
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ag-bg: #0B1220;
        --ag-panel: #111C2E;
        --ag-panel-alt: #152238;
        --ag-border: #26364D;
        --ag-text: #EDF2FA;
        --ag-muted: #91A1B8;
        --ag-blue: #78A6FF;
        --ag-violet: #A78BFA;
        --ag-green: #4DD4A2;
        --ag-red: #FF7185;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(ellipse at 75% -15%, rgba(74, 105, 164, 0.13), transparent 38%),
            var(--ag-bg);
        color: var(--ag-text);
    }

    [data-testid="stHeader"] {
        background: rgba(11, 18, 32, 0.92);
    }

    [data-testid="stSidebar"] {
        background: #0E1929;
        border-right: 1px solid var(--ag-border);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.35rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--ag-text) !important;
        letter-spacing: -0.035em;
    }

    h1 { font-size: 2.15rem !important; }
    h2 { font-size: 1.55rem !important; }
    h3 { font-size: 1.15rem !important; }

    p, label, span, div {
        overflow-wrap: anywhere;
    }

    [data-testid="stMarkdownContainer"] p {
        color: #C0CCDC;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 4px 2px 2px;
    }

    .brand-mark {
        width: 36px;
        height: 36px;
        display: grid;
        place-items: center;
        border-radius: 11px;
        color: #0B1220;
        background: linear-gradient(145deg, #9CC2FF, #8B82F6);
        font-size: 20px;
        font-weight: 800;
    }

    .brand-name {
        color: #F4F7FC;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 700;
        letter-spacing: -0.8px;
    }

    .brand-subtitle {
        color: var(--ag-muted);
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.55px;
        margin: 3px 0 0 47px;
    }

    .eyebrow {
        color: #9CB3D2;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.8px;
        text-transform: uppercase;
        margin-bottom: 7px;
    }

    .page-description {
        color: var(--ag-muted);
        font-size: 14px;
        margin-top: -8px;
        margin-bottom: 22px;
    }

    .topline {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        flex-wrap: wrap;
        margin: 2px 0 22px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        border: 1px solid #315344;
        border-radius: 999px;
        padding: 6px 11px;
        color: #8DE4BD;
        background: rgba(77, 212, 162, 0.08);
        font-size: 11px;
        font-weight: 700;
        letter-spacing: .35px;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #4DD4A2;
    }

    .status-pill.mock {
        color: #F4CE83;
        border-color: #665331;
        background: rgba(246, 198, 106, 0.08);
    }

    .status-pill.mock .status-dot {
        background: #F6C66A;
    }

    .metric-card {
        background: linear-gradient(145deg, #152238, #111C2E);
        border: 1px solid var(--ag-border);
        border-radius: 14px;
        padding: 17px 18px 15px;
        min-height: 122px;
        box-shadow: 0 8px 24px rgba(0,0,0,.10);
    }

    .metric-label {
        color: #9AABC1;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
    }

    .metric-value {
        color: #F4F7FC;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 27px;
        line-height: 1.2;
        font-weight: 700;
        margin-top: 11px;
        letter-spacing: -1px;
    }

    .metric-note {
        color: #8394AA;
        font-size: 11px;
        margin-top: 7px;
    }

    .surface {
        background: #111C2E;
        border: 1px solid var(--ag-border);
        border-radius: 14px;
        padding: 18px 20px;
    }

    .surface-title {
        color: #EAF0F8;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 3px;
    }

    .surface-subtitle {
        color: #91A1B8;
        font-size: 11px;
        margin-bottom: 12px;
    }

    .agent-heading {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 10px;
    }

    .agent-name {
        color: #F2F6FC;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 600;
    }

    .agent-type {
        color: #8FA1B9;
        font-size: 11px;
        margin-top: 3px;
    }

    .result-pass, .result-fail {
        display: inline-block;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: .7px;
    }

    .result-pass {
        color: #8DE4BD;
        background: rgba(77, 212, 162, .10);
        border: 1px solid rgba(77, 212, 162, .25);
    }

    .result-fail {
        color: #FF9BA9;
        background: rgba(255, 113, 133, .10);
        border: 1px solid rgba(255, 113, 133, .25);
    }

    .sidebar-note {
        color: #8294AB;
        font-size: 11px;
        line-height: 1.55;
    }

    .stButton > button {
        min-height: 42px;
        border-radius: 9px;
        border: 1px solid #45618B;
        font-weight: 700;
        transition: all .15s ease;
    }

    .stButton > button[kind="primary"] {
        color: #091322;
        background: linear-gradient(110deg, #9CC2FF, #A99BFF);
        border: none;
    }

    .stButton > button:hover {
        border-color: #9CBFFF;
        transform: translateY(-1px);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--ag-border);
        border-radius: 10px;
        overflow: hidden;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--ag-border);
        border-radius: 10px;
        background: rgba(17, 28, 46, .55);
    }

    div[data-testid="stCodeBlock"] {
        border: 1px solid var(--ag-border);
        border-radius: 10px;
    }

    [data-baseweb="tab-list"] {
        gap: 8px;
    }

    [data-baseweb="tab"] {
        border-radius: 8px;
    }

    hr {
        border-color: var(--ag-border);
    }

    .footer {
        color: #71839C;
        font-size: 11px;
        text-align: center;
        padding: 22px 0 8px;
    }

    @media (max-width: 800px) {
        h1 { font-size: 1.75rem !important; }
        .metric-card { min-height: 108px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATA HELPERS
# ============================================================

def load_result(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_result(result: dict) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = RESULTS_DIR / f"benchmark_live_{timestamp}.json"
    path.write_text(json.dumps(result, indent=4), encoding="utf-8")
    return path


def safe_float(value, default=0.0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default


def format_seconds(value) -> str:
    return f"{safe_float(value):.3f} s"


def result_is_mock(result: dict) -> bool:
    return "MOCK" in str(result.get("execution_mode", "")).upper()


def metric_card(label: str, value: str, note: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="margin: 8px 0 13px;">
            <div class="surface-title">{title}</div>
            <div class="surface-subtitle">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_badge(success: bool) -> str:
    if success:
        return '<span class="result-pass">PASSED</span>'
    return '<span class="result-fail">FAILED</span>'


def show_agent_card(agent: dict, title: str, description: str):
    status_html = status_badge(bool(agent.get("success")))
    st.markdown(
        f"""
        <div class="surface">
            <div class="agent-heading">
                <div>
                    <div class="agent-name">{title}</div>
                    <div class="agent-type">{description}</div>
                </div>
                {status_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)
    with a:
        st.metric("Attempts", agent.get("attempts", "—"))
    with b:
        st.metric("Latency", format_seconds(agent.get("latency_seconds")))
    with c:
        st.metric("Test time", format_seconds(agent.get("test_latency_seconds")))

    with st.expander(f"Inspect {title} generated code"):
        st.code(agent.get("code", "# No code recorded"), language="python")

    test_result = agent.get("test_result", {})
    with st.expander(f"View {title} test output"):
        st.text(test_result.get("stdout") or "No standard output recorded.")
        if test_result.get("stderr"):
            st.error(test_result["stderr"])
        elif test_result.get("passed"):
            st.success("No test errors reported.")
        else:
            st.caption("No additional error details recorded.")


def chart_layout(fig, height=300):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#C6D2E2", size=11),
        title=dict(font=dict(family="Space Grotesk, sans-serif", size=15, color="#EDF2FA")),
        margin=dict(l=12, r=18, t=48, b=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10),
        ),
        hoverlabel=dict(
            bgcolor="#17263B",
            bordercolor="#405573",
            font=dict(color="#F4F7FC", family="DM Sans"),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(145,161,184,.12)",
        zeroline=False,
        linecolor="rgba(145,161,184,.18)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(145,161,184,.12)",
        zeroline=False,
        linecolor="rgba(145,161,184,.18)",
    )
    return fig


def render_comparison_chart(title: str, subtitle: str, metric_label: str,
                            direct_value: float, verify_value: float,
                            suffix: str, color_direct: str = BLUE,
                            color_verify: str = VIOLET):
    section_heading(title, subtitle)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="DirectCoder",
            x=[direct_value],
            y=["DirectCoder"],
            orientation="h",
            marker=dict(color=color_direct, line=dict(width=0)),
            text=[f"{direct_value:.3f}{suffix}"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"DirectCoder<br>{metric_label}: %{{x:.3f}}{suffix}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            name="VerifyCoder",
            x=[verify_value],
            y=["VerifyCoder"],
            orientation="h",
            marker=dict(color=color_verify, line=dict(width=0)),
            text=[f"{verify_value:.3f}{suffix}"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"VerifyCoder<br>{metric_label}: %{{x:.3f}}{suffix}<extra></extra>",
        )
    )
    fig.update_layout(barmode="group", showlegend=False)
    fig.update_xaxes(title=metric_label, rangemode="tozero")
    fig.update_yaxes(title=None, showgrid=False, categoryorder="array",
                     categoryarray=["VerifyCoder", "DirectCoder"])
    fig = chart_layout(fig, height=235)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand-lockup">
            <div class="brand-mark">◈</div>
            <div class="brand-name">AgentGauge</div>
        </div>
        <div class="brand-subtitle">AI BENCHMARK STUDIO</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("WORKSPACE")

    page = st.radio(
        "Navigation",
        ["Overview", "Run Benchmark", "Agent Comparison", "Benchmark History"],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("BENCHMARKED WORKFLOWS")

    st.markdown(
        """
        <div style="padding:9px 0 11px;">
            <div style="display:flex;align-items:center;gap:9px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#78A6FF;"></span>
                <b style="color:#EAF0F8;font-size:13px;">DirectCoder</b>
            </div>
            <div class="sidebar-note" style="padding-left:17px;">Single-pass generation</div>
        </div>
        <div style="padding:4px 0 11px;">
            <div style="display:flex;align-items:center;gap:9px;">
                <span style="width:8px;height:8px;border-radius:50%;background:#A78BFA;"></span>
                <b style="color:#EAF0F8;font-size:13px;">VerifyCoder</b>
            </div>
            <div class="sidebar-note" style="padding-left:17px;">Generate · test · repair</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()
    st.caption("SYSTEM")
    st.markdown(
        '<div class="status-pill"><span class="status-dot"></span>Benchmark engine ready</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sidebar-note" style="margin-top:9px;">Gemini API availability can vary. '
        'Offline demo mode is available for presentations.</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# LOAD RESULT FILES
# ============================================================

result_files = sorted(
    RESULTS_DIR.glob("benchmark_*.json"),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)

selected_result = None
active_result = st.session_state.get("active_result")

if active_result:
    active_path = Path(active_result)
    if active_path.exists():
        try:
            selected_result = load_result(active_path)
        except (OSError, json.JSONDecodeError):
            selected_result = None

if selected_result is None and result_files:
    try:
        selected_result = load_result(result_files[0])
        st.session_state["active_result"] = str(result_files[0])
    except (OSError, json.JSONDecodeError):
        selected_result = None

is_mock = bool(selected_result and result_is_mock(selected_result))


# ============================================================
# SHARED PAGE HEADER
# ============================================================

page_meta = {
    "Overview": ("WORKSPACE OVERVIEW", "A focused view of your latest agent evaluation."),
    "Run Benchmark": ("NEW EVALUATION", "Configure a task, execute both workflows and save the results."),
    "Agent Comparison": ("PERFORMANCE ANALYTICS", "Inspect how the two coding-agent workflows behave."),
    "Benchmark History": ("RUN ARCHIVE", "Review saved benchmark executions and their outcomes."),
}

eyebrow, description = page_meta[page]
st.markdown(
    f"""
    <div class="topline">
        <div class="eyebrow">{eyebrow}</div>
        <div class="status-pill {'mock' if is_mock else ''}">
            <span class="status-dot"></span>
            {'OFFLINE DEMONSTRATION' if is_mock else 'BENCHMARK WORKSPACE'}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(f'<div class="page-description">{description}</div>', unsafe_allow_html=True)


# ============================================================
# PAGE: OVERVIEW
# ============================================================

if page == "Overview":
    st.title("Agent performance, measured.")
    st.markdown(
        '<div class="page-description">Understand whether an AI coding workflow delivers working, test-verified code.</div>',
        unsafe_allow_html=True,
    )

    if selected_result:
        direct = selected_result["direct_coder"]
        verify = selected_result["verify_coder"]
        mode = selected_result.get("execution_mode", "LIVE GEMINI RESULT")

        if result_is_mock(selected_result):
            st.warning(
                "You are viewing a controlled offline demonstration. "
                "These results are simulated workflow examples, not live Gemini measurements."
            )
        else:
            st.success("A benchmark result is loaded.")

        passed_agents = int(bool(direct.get("success"))) + int(bool(verify.get("success")))
        total_attempts = int(direct.get("attempts", 0)) + int(verify.get("attempts", 0))
        timestamp = selected_result.get("timestamp", "Timestamp unavailable")
        if timestamp != "Timestamp unavailable":
            try:
                timestamp = datetime.fromisoformat(timestamp).strftime("%d %b %Y · %I:%M %p")
            except (ValueError, TypeError):
                pass

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Workflows evaluated", "02", "DirectCoder and VerifyCoder")
        with c2:
            metric_card("Workflows passed", f"{passed_agents}/2", "Based on final test outcomes")
        with c3:
            metric_card("Total attempts", str(total_attempts), "Across both workflows")
        with c4:
            metric_card("Execution mode", "MOCK" if result_is_mock(selected_result) else "LIVE", "See run details for context")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Latest evaluation")
        st.caption(f"{mode}  ·  {timestamp}")

        left, right = st.columns(2, gap="large")
        with left:
            show_agent_card(
                direct,
                "DirectCoder",
                "Single-pass generation · one generation attempt",
            )
        with right:
            show_agent_card(
                verify,
                "VerifyCoder",
                "Test-guided generation · bounded correction loop",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Evaluation workflow")
        flow1, flow2, flow3 = st.columns(3, gap="medium")
        with flow1:
            st.markdown(
                '<div class="surface"><div class="eyebrow">01 / GENERATE</div>'
                '<div class="surface-title">Same task, same conditions</div>'
                '<div class="surface-subtitle">Both workflows receive the same programming task and test suite.</div></div>',
                unsafe_allow_html=True,
            )
        with flow2:
            st.markdown(
                '<div class="surface"><div class="eyebrow">02 / VERIFY</div>'
                '<div class="surface-title">Execute the test suite</div>'
                '<div class="surface-subtitle">Generated code is checked against the supplied tests.</div></div>',
                unsafe_allow_html=True,
            )
        with flow3:
            st.markdown(
                '<div class="surface"><div class="eyebrow">03 / ANALYSE</div>'
                '<div class="surface-title">Compare workflow outcomes</div>'
                '<div class="surface-subtitle">Correctness, latency and correction effort are presented together.</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No benchmark results are available yet. Open Run Benchmark and load the offline demonstration or run a live benchmark.")


# ============================================================
# PAGE: RUN BENCHMARK
# ============================================================

elif page == "Run Benchmark":
    st.title("Configure an evaluation")

    with st.container(border=True):
        st.markdown("### Benchmark configuration")
        st.caption("Start with the included palindrome scenario or replace it with your own Python task.")

        task = st.text_area("Programming task", value=TASK.strip(), height=165)
        tests = st.text_area("Python test suite", value=TEST_CODE.strip(), height=205)

        opt1, opt2 = st.columns(2)
        with opt1:
            max_attempts = st.slider(
                "VerifyCoder maximum attempts",
                min_value=1,
                max_value=3,
                value=3,
                help="Maximum number of generation/correction attempts for VerifyCoder.",
            )
        with opt2:
            timeout = st.slider(
                "Test execution timeout (seconds)",
                min_value=1,
                max_value=15,
                value=5,
            )

        run_live = st.button("Run live Gemini benchmark", type="primary", use_container_width=True)

    if run_live:
        if not task.strip() or not tests.strip():
            st.error("Please provide both a programming task and a test suite.")
        else:
            try:
                with st.spinner("Running both workflows. Gemini may take several minutes..."):
                    result = run_benchmark(
                        task=task,
                        test_code=tests,
                        max_attempts=max_attempts,
                        timeout=timeout,
                    )
                    result["execution_mode"] = "LIVE GEMINI"
                    result["timestamp"] = datetime.now().astimezone().isoformat()
                    result["benchmark_id"] = datetime.now().strftime("benchmark_%Y%m%d_%H%M%S")
                    saved_path = save_result(result)

                st.session_state["active_result"] = str(saved_path)
                st.success("Benchmark completed and saved.")
                st.json(
                    {
                        "DirectCoder passed": result["direct_coder"]["success"],
                        "VerifyCoder passed": result["verify_coder"]["success"],
                        "Saved result": str(saved_path),
                    }
                )
            except Exception as error:
                st.error(f"Benchmark could not complete: {error}")
                st.info(
                    "This may be a temporary Gemini availability issue. "
                    "Your previously saved benchmark results have not been changed."
                )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## Presentation mode")
    st.markdown(
        '<div class="surface"><div class="surface-title">Load the prepared offline demonstration</div>'
        '<div class="surface-subtitle">Uses saved mock agent responses and the local test runner. '
        'It does not make a Gemini API request.</div></div>',
        unsafe_allow_html=True,
    )
    if st.button("Load offline demonstration", use_container_width=True):
        if DEMO_FILE.exists():
            st.session_state["active_result"] = str(DEMO_FILE)
            st.success("Offline demonstration loaded.")
            st.rerun()
        else:
            st.error("Offline demonstration file not found in the results folder.")


# ============================================================
# PAGE: AGENT COMPARISON
# ============================================================

elif page == "Agent Comparison":
    st.title("Workflow comparison")

    if not selected_result:
        st.info("Load or run a benchmark to see the comparison.")
    else:
        direct = selected_result["direct_coder"]
        verify = selected_result["verify_coder"]

        if result_is_mock(selected_result):
            st.warning(
                "Offline mock demonstration: use these values to explain the dashboard workflow, "
                "not as evidence of live Gemini performance."
            )

        # Outcome summary
        st.markdown("## Outcome at a glance")
        outcome1, outcome2 = st.columns(2, gap="large")
        with outcome1:
            st.markdown(
                f'<div class="surface"><div class="agent-heading">'
                f'<div><div class="agent-name">DirectCoder</div>'
                f'<div class="agent-type">Single-pass generation</div></div>'
                f'{status_badge(bool(direct.get("success")))}</div>'
                f'<div style="color:#91A1B8;font-size:12px;margin-top:8px;">'
                f'Attempts: <b style="color:#EDF2FA">{direct.get("attempts", "—")}</b>'
                f' &nbsp; · &nbsp; Latency: <b style="color:#EDF2FA">{format_seconds(direct.get("latency_seconds"))}</b>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        with outcome2:
            st.markdown(
                f'<div class="surface"><div class="agent-heading">'
                f'<div><div class="agent-name">VerifyCoder</div>'
                f'<div class="agent-type">Generate, test and repair</div></div>'
                f'{status_badge(bool(verify.get("success")))}</div>'
                f'<div style="color:#91A1B8;font-size:12px;margin-top:8px;">'
                f'Attempts: <b style="color:#EDF2FA">{verify.get("attempts", "—")}</b>'
                f' &nbsp; · &nbsp; Latency: <b style="color:#EDF2FA">{format_seconds(verify.get("latency_seconds"))}</b>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Performance analytics")
        st.caption("Each chart compares one metric at a time. Lower values are not automatically better for every metric.")

        chart_left, chart_right = st.columns(2, gap="large")
        with chart_left:
            render_comparison_chart(
                "End-to-end latency",
                "Total time recorded for each agent workflow.",
                "Latency (seconds)",
                safe_float(direct.get("latency_seconds")),
                safe_float(verify.get("latency_seconds")),
                " s",
            )
        with chart_right:
            render_comparison_chart(
                "Correction attempts",
                "Number of generation/correction attempts used.",
                "Attempts",
                safe_float(direct.get("attempts")),
                safe_float(verify.get("attempts")),
                "",
                color_direct=BLUE,
                color_verify=VIOLET,
            )

        chart_left2, chart_right2 = st.columns(2, gap="large")
        with chart_left2:
            render_comparison_chart(
                "Test execution time",
                "Time spent executing the test suite, separate from generation.",
                "Test time (seconds)",
                safe_float(direct.get("test_latency_seconds")),
                safe_float(verify.get("test_latency_seconds")),
                " s",
                color_direct=BLUE,
                color_verify=VIOLET,
            )

        with chart_right2:
            section_heading(
                "Correctness outcome",
                "Final test result for each workflow. This is categorical, not a continuous score.",
            )
            correctness_rows = []
            for name, agent in [("DirectCoder", direct), ("VerifyCoder", verify)]:
                correctness_rows.append(
                    {
                        "Agent": name,
                        "Outcome": "Passed" if agent.get("success") else "Failed",
                        "Status": 1 if agent.get("success") else 0,
                    }
                )
            correctness_df = pd.DataFrame(correctness_rows)
            st.dataframe(
                correctness_df[["Agent", "Outcome"]],
                hide_index=True,
                use_container_width=True,
            )
            for name, agent in [("DirectCoder", direct), ("VerifyCoder", verify)]:
                passed = bool(agent.get("success"))
                color = GREEN if passed else RED
                label = "PASS" if passed else "FAIL"
                st.markdown(
                    f'<div style="display:flex;align-items:center;justify-content:space-between;'
                    f'padding:9px 2px;border-bottom:1px solid {BORDER};">'
                    f'<span style="color:#C6D2E2;font-size:12px;">{name}</span>'
                    f'<span style="color:{color};font-weight:800;font-size:11px;letter-spacing:1px;">{label}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # Token data is optional; never plot missing or fabricated values.
        direct_tokens = direct.get("total_tokens")
        verify_tokens = verify.get("total_tokens")
        if direct_tokens is not None and verify_tokens is not None:
            st.markdown("<br>", unsafe_allow_html=True)
            token_left, token_right = st.columns(2, gap="large")
            with token_left:
                render_comparison_chart(
                    "Total token usage",
                    "Reported token counts for each workflow.",
                    "Tokens",
                    safe_float(direct_tokens),
                    safe_float(verify_tokens),
                    "",
                )
            with token_right:
                section_heading("Token availability", "Token counts are shown only when supplied by the model response.")
                st.metric("DirectCoder tokens", f"{int(safe_float(direct_tokens)):,}")
                st.metric("VerifyCoder tokens", f"{int(safe_float(verify_tokens)):,}")
        else:
            st.caption("Token comparison is hidden because complete token-usage data is unavailable for this run.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Generated code")
        code_tab1, code_tab2 = st.tabs(["DirectCoder output", "VerifyCoder output"])
        with code_tab1:
            st.code(direct.get("code", "# No code recorded"), language="python")
        with code_tab2:
            st.code(verify.get("code", "# No code recorded"), language="python")


# ============================================================
# PAGE: BENCHMARK HISTORY
# ============================================================

elif page == "Benchmark History":
    st.title("Benchmark history")
    st.caption("A local archive of saved benchmark result files.")

    if not result_files:
        st.info("No saved benchmark results found yet.")
    else:
        rows = []
        for path in result_files:
            try:
                data = load_result(path)
                direct = data["direct_coder"]
                verify = data["verify_coder"]
                rows.append(
                    {
                        "Benchmark": data.get("benchmark_id", path.stem),
                        "Mode": data.get("execution_mode", "LIVE GEMINI"),
                        "DirectCoder": "PASS" if direct.get("success") else "FAIL",
                        "VerifyCoder": "PASS" if verify.get("success") else "FAIL",
                        "Verify attempts": verify.get("attempts", "—"),
                        "File": path.name,
                        "Path": path,
                    }
                )
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue

        if rows:
            history_df = pd.DataFrame(rows)
            st.markdown("## Saved evaluations")
            st.dataframe(
                history_df.drop(columns=["Path", "File"]),
                hide_index=True,
                use_container_width=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("## Open a previous result")
            selected_file = st.selectbox("Choose a benchmark", [row["File"] for row in rows])
            if st.button("Open selected benchmark", type="primary", use_container_width=True):
                selected_path = RESULTS_DIR / selected_file
                st.session_state["active_result"] = str(selected_path)
                st.success("Selected benchmark loaded.")
                st.rerun()
        else:
            st.warning("No readable benchmark result files were found.")


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">AGENTGAUGE AI &nbsp;·&nbsp; Know which AI agent actually delivers.</div>',
    unsafe_allow_html=True,
)
