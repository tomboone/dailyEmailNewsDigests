"""Email building and sending for dailyemailnewsdigests."""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

import src.dailyemailnewsdigests.config as config


def build_html_email(subject: str, date_str: str, sections: list[dict[str, Any]]) -> str:
    """Build a styled HTML email body from sections.

    Args:
        subject: The email subject line (used in header and footer).
        date_str: Formatted date string for the header.
        sections: List of dicts with 'title' and 'items' keys. Each item has
            'source', 'title', 'link', and 'description'.

    Returns:
        The complete HTML email body.
    """
    outer_open = (
        "<html><body style='margin:0;padding:0;background-color:#f4f4f7;"
        "font-family:Arial,Helvetica,sans-serif;color:#333333;'>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' "
        "style='background-color:#f4f4f7;'><tr><td align='center' "
        "style='padding:24px 16px;'>"
    )

    title_table = (
        "<table role='presentation' width='600' cellpadding='0' cellspacing='0' "
        "style='background-color:#1a1a2e;border-radius:8px 8px 0 0;overflow:hidden;'>"
        "<tr><td style='padding:32px 40px;'>"
        f"<h1 style='margin:0;font-size:24px;font-weight:700;color:#ffffff;"
        f"letter-spacing:-0.3px;'>{subject}</h1>"
        f"<p style='margin:6px 0 0;font-size:14px;color:#a0a0b8;'>{date_str}</p>"
        "</td></tr></table>"
    )

    footer = (
        "<table role='presentation' width='600' cellpadding='0' cellspacing='0' "
        "style='background-color:#f9f9fb;border-radius:0 0 8px 8px;"
        "border-top:1px solid #eeeeee;'>"
        "<tr><td style='padding:20px 40px;'>"
        "<p style='margin:0;font-size:12px;color:#999999;text-align:center;'>"
        f"You received this email because you are subscribed to {subject}."
        "</p></td></tr></table>"
        "</td></tr></table></body></html>"
    )

    parts = [outer_open, title_table]

    for section in sections:
        section_title = section["title"]
        items: list[dict[str, str]] = section["items"]

        # Category header
        parts.append(
            "<table role='presentation' width='600' cellpadding='0' cellspacing='0' "
            "style='margin-top:20px;'>"
            "<tr><td style='background-color:#6c63ff;padding:14px 40px;"
            "border-radius:8px 8px 0 0;'>"
            f"<h2 style='margin:0;font-size:16px;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:1.5px;color:#ffffff;'>"
            f"{section_title}</h2>"
            "</td></tr></table>"
        )

        # Items table
        parts.append(
            "<table role='presentation' width='600' cellpadding='0' cellspacing='0' "
            "style='background-color:#ffffff;border-radius:0 0 8px 8px;overflow:hidden;"
            "box-shadow:0 1px 3px rgba(0,0,0,0.08);'>"
        )

        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            padding = "20px 40px 28px" if is_last else "20px 40px"

            parts.append(
                f"<tr><td style='padding:{padding};'>"
                f"<p style='margin:0 0 4px;font-size:12px;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:0.5px;color:#999999;'>"
                f"{item.get('source', '')}</p>"
                f"<a href='{item.get('link', '#')}' style='font-size:17px;"
                f"font-weight:700;color:#1a1a2e;text-decoration:none;"
                f"line-height:1.3;'>{item.get('title', '')}</a>"
                f"<p style='margin:8px 0 0;font-size:14px;line-height:1.6;"
                f"color:#555555;'>{item.get('description', '')}</p>"
                "</td></tr>"
            )

            if not is_last:
                parts.append(
                    "<tr><td style='padding:0 40px;'>"
                    "<hr style='border:none;border-top:1px solid #eeeeee;"
                    "margin:0;' /></td></tr>"
                )

        parts.append("</table>")

    parts.append(footer)
    return "".join(parts)


def build_plain_text_email(subject: str, sections: list[dict[str, Any]]) -> str:
    """Build a plain text email body from sections.

    Args:
        subject: The email subject line.
        sections: List of dicts with 'title' and 'items' keys.

    Returns:
        The plain text email body.
    """
    parts = [f"{subject}\n\n"]
    for section in sections:
        parts.append(f"--- {section['title']} ---\n\n")
        for item in section["items"]:
            parts.append(
                f"{item.get('source', '')}\n{item.get('title', '')}\n{item.get('link', '')}\n\n"
            )
    return "".join(parts)


def send_smtp_email(
    subject: str,
    text_body: str,
    html_body: str,
    sender: str,
    recipient: str,
) -> None:
    """Construct and send a multipart email via SMTP.

    Args:
        subject: The email subject.
        text_body: The plain text email body.
        html_body: The HTML email body.
        sender: The sender's email address.
        recipient: The recipient's email address.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recipient

    message.attach(MIMEText(text_body))
    message.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP(config.SMTP_SERVER, port=config.SMTP_PORT) as server:
        server.starttls(context=context)
        server.login(config.SMTP_USER, config.SMTP_PWD)
        server.sendmail(sender, recipient, message.as_string())
