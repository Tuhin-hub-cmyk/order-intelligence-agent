import streamlit as st
import pandas as pd
from src.data_loader import load_orders
from src.analyzer import analyse_orders
from src.agent import ask_agent

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Atlas Copco — Order Intelligence Agent",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load and analyse data (cached for 5 minutes) ──────────────────────────────
@st.cache_data(ttl=300)
def get_data():
    df = load_orders()
    df, summary, priorities = analyse_orders(df)
    return df, summary, priorities

df, summary, priorities = get_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Atlas Copco")
    st.caption("Vacuum Technique — Australia")
    st.divider()

    st.markdown("### Today's Summary")
    st.metric("Total Orders", summary["total_orders"])

    col1, col2 = st.columns(2)
    col1.metric("Overdue", summary["overdue_count"])
    col2.metric("Blocked", summary["blocked_count"])
    col1.metric("At Risk", summary["at_risk_count"])
    col2.metric("Completed", summary["completed_count"])

    st.metric(
        "Value at Risk",
        f"${summary['total_value_at_risk_aud']:,} AUD",
    )

    st.divider()

    # Top priorities panel
    st.markdown("### Top Priorities")
    flag_icons = {
        "OVERDUE": "🔴",
        "BLOCKED": "🟠",
        "AT_RISK": "🟡",
        "STALE": "🔵",
        "ON_TRACK": "🟢",
    }
    for order in priorities:
        icon = flag_icons.get(order["flag"], "⚪")
        st.markdown(
            f"{icon} **{order['order_id']}** — {order['customer_name']}"
        )
        st.caption(
            f"{order['assigned_to']} · {order['days_until_due']} days"
        )

    st.divider()

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ── Main content ──────────────────────────────────────────────────────────────
st.title("Order Intelligence Agent")
st.caption(
    "AI-powered sales and service order management "
    "— Vacuum Technique Australia"
)

tab1, tab2 = st.tabs(["📋 Orders Dashboard", "🤖 AI Assistant"])

# ── Tab 1: Orders Dashboard ───────────────────────────────────────────────────
with tab1:

    # Top metric row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Orders", summary["total_orders"])
    col2.metric("Overdue", summary["overdue_count"])
    col3.metric("Blocked", summary["blocked_count"])
    col4.metric("Value at Risk", f"${summary['total_value_at_risk_aud']:,}")

    st.divider()

    # Flag filter
    selected_flags = st.multiselect(
        "Filter by flag",
        options=["OVERDUE", "BLOCKED", "AT_RISK", "STALE", "ON_TRACK", "COMPLETED"],
        default=["OVERDUE", "BLOCKED", "AT_RISK"],
    )

    filtered_df = (
        df[df["flag"].isin(selected_flags)] if selected_flags else df
    )

    # Build clean display table
    display_df = filtered_df[[
        "order_id", "customer_name", "order_type", "status",
        "flag", "priority", "days_until_due", "assigned_to",
        "value_aud", "delay_reason",
    ]].copy()
    display_df.insert(
        6, "due_date", filtered_df["due_date"].dt.strftime("%Y-%m-%d")
    )

    # Colour coding by flag
    def colour_rows(row):
        colours = {
            "OVERDUE":   "background-color: #ffebee",
            "BLOCKED":   "background-color: #fff3e0",
            "AT_RISK":   "background-color: #fffde7",
            "STALE":     "background-color: #e3f2fd",
            "COMPLETED": "background-color: #e8f5e9",
        }
        return [colours.get(row["flag"], "")] * len(row)

    st.dataframe(
        display_df.style.apply(colour_rows, axis=1),
        use_container_width=True,
        height=480,
    )

    st.caption(f"Showing {len(filtered_df)} of {len(df)} orders")

# ── Tab 2: AI Assistant ───────────────────────────────────────────────────────
with tab2:

    st.subheader("Ask about your orders")
    st.caption(
        "Type a natural language question about order status, "
        "delays, priorities, or team workload."
    )

    # Initialise session state for chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent_history" not in st.session_state:
        st.session_state.agent_history = []

    # Example question buttons — only shown when chat is empty
    if not st.session_state.messages:
        st.markdown("**Try one of these:**")
        examples = [
            "Which orders need attention today?",
            "What is blocking the Woodside Energy order?",
            "Who has the most urgent workload right now?",
            "Summarise all overdue orders and their delay reasons",
            "Which orders are escalated and what needs to happen today?",
        ]
        col1, col2 = st.columns(2)
        for i, example in enumerate(examples):
            if (col1 if i % 2 == 0 else col2).button(
                example, key=f"ex_{i}", use_container_width=True
            ):
                st.session_state["pending"] = example
                st.rerun()

    # Retrieve and clear any pending question from example buttons
    pending = st.session_state.get("pending", None)
    if pending:
        del st.session_state["pending"]

    # Display existing chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input — also accepts pending question from buttons
    question = st.chat_input("Ask a question about your orders...") or pending

    if question:
        # Show the user's question
        with st.chat_message("user"):
            st.markdown(question)
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        # Get and display AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer, st.session_state.agent_history = ask_agent(
                    question, df, summary, st.session_state.agent_history
                )
            st.markdown(answer)
        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    # Clear conversation button
    if st.session_state.messages:
        st.divider()
        if st.button("🗑️ Clear conversation", use_container_width=False):
            st.session_state.messages = []
            st.session_state.agent_history = []
            st.rerun()