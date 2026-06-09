import io
import streamlit as st
import pandas as pd
from src.data_loader import load_orders
from src.analyzer import analyse_orders
from src.agent import ask_agent
from src.emailer import send_alert_email

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OrderIQ — Intelligent Order Management",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .project-header {
        padding: 1.5rem 2rem;
        background: linear-gradient(135deg, #1e3a5f 0%, #1d4ed8 100%);
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .project-header h1 {
        color: #ffffff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .project-header p {
        color: #bfdbfe;
        font-size: 0.9rem;
        margin: 0.3rem 0 0 0;
    }
    .creator-badge {
        display: inline-block;
        background: rgba(255,255,255,0.15);
        color: #e0f2fe;
        font-size: 0.75rem;
        padding: 0.2rem 0.75rem;
        border-radius: 20px;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    [data-testid="metric-container"] {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 0.75rem 1rem;
    }
    [data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-size: 0.8rem !important;
    }
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #f1f5f9 !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        background: #1e293b;
        border-radius: 8px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }
    .upload-info {
        background: #1e293b;
        border: 1px dashed #3b82f6;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 0.5rem;
        line-height: 1.6;
    }
    .footer-credit {
        text-align: center;
        color: #475569;
        font-size: 0.75rem;
        padding: 2rem 0 0.5rem 0;
        border-top: 1px solid #1e293b;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ────────────────────────────────────────────────────
if "uploaded_bytes" not in st.session_state:
    st.session_state.uploaded_bytes = None
if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_history" not in st.session_state:
    st.session_state.agent_history = []
if "load_error" not in st.session_state:
    st.session_state.load_error = None

# ── Load and analyse data ─────────────────────────────────────────────────────
def load_and_analyse(uploaded_file=None):
    df = load_orders(uploaded_file)
    df, summary, priorities = analyse_orders(df)
    return df, summary, priorities

try:
    if st.session_state.uploaded_bytes is not None:
        file_obj = io.BytesIO(st.session_state.uploaded_bytes)
        df, summary, priorities = load_and_analyse(file_obj)
    else:
        df, summary, priorities = load_and_analyse(None)
    st.session_state.load_error = None
except ValueError as e:
    st.session_state.load_error = str(e)
    df, summary, priorities = load_and_analyse(None)
except Exception:
    st.session_state.load_error = (
        "Something went wrong reading your file. "
        "Please make sure it is a valid CSV and try again."
    )
    df, summary, priorities = load_and_analyse(None)

# ── CSV template ──────────────────────────────────────────────────────────────
def get_template_csv() -> bytes:
    template = pd.DataFrame([{
        "order_id":      "SO-2026-001",
        "customer_name": "Example Company Pty Ltd",
        "order_type":    "Sales Order",
        "status":        "Blocked",
        "priority":      "High",
        "created_date":  "2026-04-15",
        "due_date":      "2026-05-20",
        "assigned_to":   "Sarah Chen",
        "product":       "Product Name Here",
        "value_aud":     45000,
        "last_updated":  "2026-05-28",
        "delay_reason":  "Awaiting customer approval",
        "notes":         "Brief operational note here",
    }])
    return template.to_csv(index=False).encode("utf-8")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 OrderIQ")
    st.caption("Intelligent Order Management System")
    st.divider()

    st.markdown("#### 📁 Data Source")

    data_source = st.radio(
        "data source",
        options=["Use demo data", "Upload your own CSV"],
        label_visibility="collapsed",
    )

    if data_source == "Upload your own CSV":
        st.download_button(
            label="⬇️ Download CSV template",
            data=get_template_csv(),
            file_name="orderiq_template.csv",
            mime="text/csv",
            use_container_width=True,
        )

        uploaded = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            label_visibility="collapsed",
        )

        if uploaded is not None:
            if uploaded.name != st.session_state.uploaded_filename:
                st.session_state.uploaded_bytes    = uploaded.read()
                st.session_state.uploaded_filename = uploaded.name
                st.session_state.messages          = []
                st.session_state.agent_history     = []
                st.session_state.load_error        = None
                st.rerun()

        if st.session_state.load_error:
            st.markdown(
                f"""
                <div style='background:#2d1515;border:1px solid #ef4444;
                            border-radius:8px;padding:10px 12px;
                            font-size:0.8rem;color:#fca5a5;
                            line-height:1.6;margin-top:8px'>
                    ⚠️ <strong>Upload issue</strong><br>
                    {st.session_state.load_error}<br><br>
                    👉 Download the template above to see the
                    correct format. Showing demo data for now.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="upload-info">'
                "✅ Upload a CSV with your order data.<br>"
                "Download the template for the correct format.<br>"
                "The app works with any number of rows."
                "</div>",
                unsafe_allow_html=True,
            )

    else:
        if st.session_state.uploaded_bytes is not None:
            st.session_state.uploaded_bytes    = None
            st.session_state.uploaded_filename = None
            st.session_state.messages          = []
            st.session_state.agent_history     = []
            st.session_state.load_error        = None
            st.rerun()

    st.divider()

    st.markdown("#### Today's Summary")
    st.metric("Total Orders", summary["total_orders"])

    c1, c2 = st.columns(2)
    c1.metric("Overdue",   summary["overdue_count"])
    c2.metric("Blocked",   summary["blocked_count"])
    c1.metric("At Risk",   summary["at_risk_count"])
    c2.metric("Completed", summary["completed_count"])

    st.metric(
        "💰 Value at Risk",
        f"${summary['total_value_at_risk_aud']:,} AUD",
    )

    st.divider()

    st.markdown("#### 🚨 Top Priorities")
    flag_icons = {
        "OVERDUE": "🔴",
        "BLOCKED": "🟠",
        "AT_RISK":  "🟡",
        "STALE":    "🔵",
        "ON_TRACK": "🟢",
    }

    if priorities:
        for order in priorities:
            icon     = flag_icons.get(order.get("flag", ""), "⚪")
            order_id = order.get("order_id", "—")
            customer = order.get("customer_name", "Unknown")
            assignee = order.get("assigned_to", "Unassigned")
            days     = order.get("days_until_due", "?")
            st.markdown(f"{icon} **{order_id}**")
            st.caption(f"{customer}  \n{assignee} · {days} days")
    else:
        st.caption("No urgent orders found.")

    st.divider()

    st.markdown("#### 📧 Email Alert")
    alert_email = st.text_input(
        "Recipient email",
        placeholder="recipient@email.com",
        label_visibility="collapsed",
    )

    if st.button("📤 Send Alert Email", use_container_width=True):
        if not alert_email:
            st.warning("Please enter a recipient email address.")
        else:
            with st.spinner("Sending alert..."):
                success, message = send_alert_email(
                    to_email=alert_email,
                    summary=summary,
                    priorities=priorities,
                )
            if success:
                st.success(message)
            else:
                st.error(message)

    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.markdown("""
    <div style='margin-top:1rem;color:#475569;font-size:0.72rem;
                line-height:1.6'>
        🧠 <strong>OrderIQ v1.2</strong><br>
        Experimental AI Project<br>
        Built by T M Towhidur Rahman Tuhin<br>
        Curtin University · BIS Extension<br>
        Perth, Western Australia
    </div>
    """, unsafe_allow_html=True)

# ── Main header ───────────────────────────────────────────────────────────────
data_label = (
    f"📁 {st.session_state.uploaded_filename}"
    if st.session_state.uploaded_filename and not st.session_state.load_error
    else "🗂️ Demo data"
)

st.markdown(f"""
<div class="project-header">
    <h1>🧠 OrderIQ</h1>
    <p>Intelligent Order Management System
       — AI-powered sales and service order analysis</p>
    <span class="creator-badge">
        Experimental Project · T M Towhidur Rahman Tuhin
        · Curtin University
    </span>
    <span class="creator-badge" style="margin-left:6px">
        {data_label}
    </span>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋  Orders Dashboard", "🤖  AI Assistant"])

# ── Tab 1: Dashboard ──────────────────────────────────────────────────────────
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Orders", summary["total_orders"])
    c2.metric("Overdue",      summary["overdue_count"])
    c3.metric("Blocked",      summary["blocked_count"])
    c4.metric("Value at Risk",
              f"${summary['total_value_at_risk_aud']:,}")

    st.divider()

    selected_flags = st.multiselect(
        "Filter by flag",
        options=[
            "OVERDUE","BLOCKED","AT_RISK",
            "STALE","ON_TRACK","COMPLETED",
        ],
        default=["OVERDUE","BLOCKED","AT_RISK"],
    )

    filtered_df = (
        df[df["flag"].isin(selected_flags)] if selected_flags else df
    )

    preferred_cols = [
        "order_id","customer_name","order_type","status",
        "flag","priority","days_until_due","assigned_to",
        "value_aud","delay_reason",
    ]
    display_cols = [c for c in preferred_cols if c in filtered_df.columns]
    display_df   = filtered_df[display_cols].copy()

    if "due_date" in filtered_df.columns:
        display_df.insert(
            min(6, len(display_df.columns)),
            "due_date",
            filtered_df["due_date"].dt.strftime("%Y-%m-%d"),
        )

    def colour_rows(row):
        colours = {
            "OVERDUE":   "background-color:#3b0f0f;color:#fca5a5",
            "BLOCKED":   "background-color:#3b1f0a;color:#fdba74",
            "AT_RISK":   "background-color:#3b3000;color:#fde68a",
            "STALE":     "background-color:#0a1f3b;color:#93c5fd",
            "COMPLETED": "background-color:#0a2e1a;color:#86efac",
        }
        if "flag" in row:
            return [colours.get(row["flag"], "")] * len(row)
        return [""] * len(row)

    st.dataframe(
        display_df.style.apply(colour_rows, axis=1),
        use_container_width=True,
        height=500,
    )
    st.caption(f"Showing {len(filtered_df)} of {len(df)} orders")

# ── Tab 2: AI Assistant ───────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🤖 Ask about your orders")
    st.caption(
        "Ask anything — natural language, typos included. "
        "The AI understands context and gives business-ready answers."
    )

    if not st.session_state.messages:
        st.markdown("**Try one of these:**")
        examples = [
            "Which orders need attention today?",
            "Whats blocking the most urgent order?",
            "Who has the most urgent workload right now?",
            "Summarise all overdue orders and delay reasons",
            "What is the total value at risk and why?",
        ]
        c1, c2 = st.columns(2)
        for i, ex in enumerate(examples):
            if (c1 if i % 2 == 0 else c2).button(
                ex, key=f"ex_{i}", use_container_width=True
            ):
                st.session_state["pending"] = ex
                st.rerun()

    pending = st.session_state.get("pending", None)
    if pending:
        del st.session_state["pending"]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = (
        st.chat_input("Ask about orders, delays, workload, priorities...")
        or pending
    )

    if question:
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("assistant"):
            with st.spinner("Analysing orders..."):
                try:
                    answer, st.session_state.agent_history = ask_agent(
                        question, df, summary,
                        st.session_state.agent_history,
                    )
                    st.markdown(answer)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": answer}
                    )
                except Exception:
                    err = (
                        "I wasn't able to process that right now. "
                        "Please try again or rephrase your question."
                    )
                    st.warning(err)

    if st.session_state.messages:
        st.divider()
        if st.button("🗑️ Clear conversation"):
            st.session_state.messages = []
            st.session_state.agent_history = []
            st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-credit">
    🧠 OrderIQ v1.2 — Experimental AI Project &nbsp;·&nbsp;
    Built by <strong>T M Towhidur Rahman Tuhin</strong>
    &nbsp;·&nbsp; Curtin University, Perth WA
    &nbsp;·&nbsp; BIS Extension 2025–2026
</div>
""", unsafe_allow_html=True)
