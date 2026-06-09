import os
import resend
from dotenv import load_dotenv

load_dotenv()


def build_email_html(summary: dict, priorities: list) -> str:
    """Build a professional HTML email with order alert details."""

    flag_colors = {
        "OVERDUE": "#ef4444",
        "BLOCKED": "#f97316",
        "AT_RISK":  "#eab308",
        "STALE":    "#3b82f6",
    }

    rows = ""
    for i, order in enumerate(priorities, 1):
        color  = flag_colors.get(order["flag"], "#94a3b8")
        reason = order.get("delay_reason", "") or "—"
        rows += f"""
        <tr>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       color:#1e293b">{i}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0">
                <span style="background:{color};color:white;padding:3px 10px;
                             border-radius:20px;font-size:11px;font-weight:600">
                    {order['flag']}
                </span>
            </td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       font-weight:600;color:#1e293b">{order['order_id']}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       color:#1e293b">{order['customer_name']}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       color:#ef4444;font-weight:600">
                {order['days_until_due']} days</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       color:#1e293b">{order['assigned_to']}</td>
            <td style="padding:10px 8px;border-bottom:1px solid #e2e8f0;
                       color:#64748b;font-size:12px">{reason}</td>
        </tr>"""

    html = f"""
    <html>
    <body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',
                 sans-serif;max-width:650px;margin:0 auto;padding:24px;
                 background:#f8fafc">

        <div style="background:linear-gradient(135deg,#1e3a5f 0%,#1d4ed8 100%);
                    padding:24px;border-radius:12px;margin-bottom:24px">
            <h1 style="color:white;margin:0;font-size:22px;font-weight:700">
                🧠 OrderIQ — Daily Alert
            </h1>
            <p style="color:#bfdbfe;margin:6px 0 0 0;font-size:13px">
                Automated order intelligence report
            </p>
        </div>

        <table width="100%" cellpadding="6" cellspacing="0"
               style="margin-bottom:24px">
            <tr>
                <td width="25%"
                    style="background:#fef2f2;border:1px solid #fecaca;
                           border-radius:10px;padding:16px;text-align:center">
                    <div style="font-size:26px;font-weight:700;color:#ef4444">
                        {summary['overdue_count']}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:4px">
                        Overdue</div>
                </td>
                <td width="4%"></td>
                <td width="25%"
                    style="background:#fff7ed;border:1px solid #fed7aa;
                           border-radius:10px;padding:16px;text-align:center">
                    <div style="font-size:26px;font-weight:700;color:#f97316">
                        {summary['blocked_count']}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:4px">
                        Blocked</div>
                </td>
                <td width="4%"></td>
                <td width="25%"
                    style="background:#fefce8;border:1px solid #fde68a;
                           border-radius:10px;padding:16px;text-align:center">
                    <div style="font-size:26px;font-weight:700;color:#eab308">
                        {summary['at_risk_count']}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:4px">
                        At Risk</div>
                </td>
                <td width="4%"></td>
                <td width="25%"
                    style="background:#eff6ff;border:1px solid #bfdbfe;
                           border-radius:10px;padding:16px;text-align:center">
                    <div style="font-size:18px;font-weight:700;color:#1d4ed8">
                        ${summary['total_value_at_risk_aud']:,}</div>
                    <div style="font-size:12px;color:#64748b;margin-top:4px">
                        AUD at Risk</div>
                </td>
            </tr>
        </table>

        <div style="background:white;border:1px solid #e2e8f0;
                    border-radius:12px;overflow:hidden;margin-bottom:24px">
            <div style="padding:16px 20px;border-bottom:1px solid #e2e8f0;
                        background:#f8fafc">
                <h2 style="margin:0;font-size:14px;font-weight:600;
                            color:#1e293b">
                    Today's Top Priorities
                </h2>
            </div>
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="font-size:13px">
                <thead>
                    <tr style="background:#f8fafc">
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">#</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Flag</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Order</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Customer</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Due</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Owner</th>
                        <th style="padding:10px 8px;text-align:left;
                                   color:#64748b;font-weight:500">Reason</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>

        <div style="text-align:center;color:#94a3b8;font-size:11px;
                    padding-top:16px;border-top:1px solid #e2e8f0">
            🧠 OrderIQ — Experimental AI Project &nbsp;·&nbsp;
            Built by T M Towhidur Rahman Tuhin &nbsp;·&nbsp;
            Curtin University, Perth WA
        </div>

    </body>
    </html>
    """
    return html


def send_alert_email(
    to_email: str,
    summary: dict,
    priorities: list,
) -> tuple[bool, str]:
    """
    Send an HTML order alert email via Resend API.

    Reads RESEND_API_KEY from environment or Streamlit secrets.

    Returns:
        (success: bool, message: str)
    """

    api_key = os.getenv("RESEND_API_KEY")

    if not api_key:
        return False, (
            "RESEND_API_KEY not configured. "
            "Please add it to your environment settings."
        )

    try:
        resend.api_key = api_key

        subject = (
            f"🧠 OrderIQ Alert — "
            f"{summary['overdue_count']} Overdue · "
            f"{summary['blocked_count']} Blocked · "
            f"${summary['total_value_at_risk_aud']:,} AUD at Risk"
        )

        params: resend.Emails.SendParams = {
            "from": "OrderIQ Alerts <onboarding@resend.dev>",
            "to": [to_email],
            "subject": subject,
            "html": build_email_html(summary, priorities),
        }

        resend.Emails.send(params)
        return True, f"Alert sent successfully to {to_email} ✓"

    except Exception as e:
        return False, f"Failed to send alert: {str(e)}"