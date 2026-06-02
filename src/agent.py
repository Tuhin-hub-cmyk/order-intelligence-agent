import os
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are an intelligent order management assistant
for an industrial company. You help the operations team manage open
sales and service orders.

You have access to today's live order data including order status,
due dates, assigned team members, delay reasons, and order values.

Your job is to:
- Answer questions about orders clearly and concisely
- Identify which orders need urgent attention
- Suggest practical next actions for the team
- Be professional, specific, and action-oriented

Important rules:
- The user may make spelling mistakes or typos — always interpret
  the intent of the question and answer it anyway
- If a question is unclear, make a reasonable assumption and answer
  based on that assumption, then mention what you assumed
- Never just repeat raw data back — interpret and give useful guidance
- Always recommend a clear next action when an order needs attention
- Keep answers concise — 3 to 6 sentences is ideal
- Always reference order IDs and customer names for specificity
- If you genuinely cannot answer, say so clearly and suggest what
  information would help
"""


def format_orders_for_context(df: pd.DataFrame, summary: dict) -> str:
    context = f"""
TODAY'S ORDER SUMMARY:
- Total Orders    : {summary['total_orders']}
- Overdue         : {summary['overdue_count']}
- Blocked         : {summary['blocked_count']}
- At Risk         : {summary['at_risk_count']}
- Stale           : {summary['stale_count']}
- On Track        : {summary['on_track_count']}
- Completed       : {summary['completed_count']}
- Value at Risk   : ${summary['total_value_at_risk_aud']:,} AUD

FULL ORDER LIST:
"""
    for _, row in df.iterrows():
        context += f"""
Order     : {row['order_id']}
Customer  : {row['customer_name']}
Type      : {row['order_type']}
Status    : {row['status']}
Flag      : {row['flag']}
Priority  : {row['priority']}
Due       : {row['due_date'].strftime('%Y-%m-%d')} ({row['days_until_due']} days)
Owner     : {row['assigned_to']}
Product   : {row['product']}
Value     : ${row['value_aud']:,} AUD
Updated   : {row['days_since_update']} days ago
Delay     : {row['delay_reason'] if row['delay_reason'] else 'None'}
Notes     : {row['notes'] if row['notes'] else 'None'}
---"""
    return context


def ask_agent(
    question: str,
    df: pd.DataFrame,
    summary: dict,
    history: list,
) -> tuple[str, list]:

    if not os.getenv("GROQ_API_KEY"):
        return (
            "Configuration error: API key not found. "
            "Please contact the system administrator.",
            history,
        )

    try:
        order_context = format_orders_for_context(df, summary)

        full_message = f"""Here is today's current order data:

{order_context}

Question: {question}"""

        history.append({"role": "user", "content": full_message})
        recent_history = history[-2:]
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + recent_history

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=1000,
        )

        answer = response.choices[0].message.content
        history.append({"role": "assistant", "content": answer})
        return answer, history

    except Exception as e:
        error_answer = (
            "I encountered a temporary issue processing your request. "
            "Please try again in a moment. If the problem persists, "
            "try rephrasing your question."
        )
        return error_answer, history