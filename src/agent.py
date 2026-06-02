import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()

# Configure the Gemini client with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# The AI's personality and instructions
SYSTEM_PROMPT = """You are an intelligent customer care assistant for 
Atlas Copco Vacuum Technique Australia.

You help the customer care team manage open sales and service orders. 
You have access to today's live order data including order status, 
due dates, assigned team members, delay reasons, and order values.

Your job is to:
- Answer questions about orders clearly and concisely
- Identify which orders need urgent attention
- Suggest practical next actions for the team
- Be professional, specific, and action-oriented

Rules:
- Never just repeat raw data back — interpret it and give useful guidance
- Always recommend a clear next action when an order needs attention
- Keep answers concise — 3 to 6 sentences is ideal
- Always use order IDs and customer names so answers are actionable
"""


def format_orders_for_context(df: pd.DataFrame, summary: dict) -> str:
    """
    Convert the DataFrame and summary into readable text
    that the AI can use as context for answering questions.
    """

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
    """
    Send a question to the Gemini AI agent with full order context.

    Args:
        question : The user's natural language question
        df       : Orders DataFrame with flags applied
        summary  : Summary statistics dictionary
        history  : Conversation history (list of message dicts)

    Returns:
        answer   : The AI's response as a string
        history  : Updated conversation history
    """

    # Check the API key exists
    if not os.getenv("GEMINI_API_KEY"):
        return (
            "Error: GEMINI_API_KEY not found. "
            "Please add it to your .env file.",
            history,
        )

    # Format order data into text context
    order_context = format_orders_for_context(df, summary)

    # Build the full message — question + data context
    full_message = f"""Here is today's current order data:

{order_context}

Question: {question}"""

    # Add to history
    history.append({"role": "user", "parts": [full_message]})

    # Keep last 6 messages to manage context size
    recent_history = history[-6:]

    # Create the Gemini model with system instructions
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )

    # Start a chat session with the recent history
    # (exclude the last message — we send that separately)
    chat = model.start_chat(history=recent_history[:-1])

    # Send the latest question
    response = chat.send_message(full_message)

    # Extract the answer
    answer = response.text

    # Add answer to history
    history.append({"role": "model", "parts": [answer]})

    return answer, history