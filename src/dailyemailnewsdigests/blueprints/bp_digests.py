""" Blueprint for retrieving and sending dailyemailnewsdigests """
import logging
import requests
import smtplib
import ssl
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict, List

import azure.functions as func

import src.dailyemailnewsdigests.config as config

bp: func.Blueprint = func.Blueprint()


def _build_html_email(subject: str, date_str: str, sections: List[dict]) -> str:
    """Build a styled HTML email body from sections.

    Args:
        subject (str): The email subject line
        date_str (str): Formatted date string for the header
        sections (list): List of dicts with 'title' and 'items' keys

    Returns:
        str: The complete HTML email body
    """
    header = (
        "<html><body style='margin:0;padding:0;background-color:#f4f4f7;"
        "font-family:Arial,Helvetica,sans-serif;color:#333333;'>"
        "<table role='presentation' width='100%' cellpadding='0' cellspacing='0' "
        "style='background-color:#f4f4f7;'><tr><td align='center' "
        "style='padding:24px 16px;'>"
        "<table role='presentation' width='600' cellpadding='0' cellspacing='0' "
        "style='background-color:#ffffff;border-radius:8px;overflow:hidden;"
        "box-shadow:0 1px 3px rgba(0,0,0,0.08);'>"
        "<tr><td style='background-color:#1a1a2e;padding:32px 40px;'>"
        f"<h1 style='margin:0;font-size:24px;font-weight:700;color:#ffffff;"
        f"letter-spacing:-0.3px;'>{subject}</h1>"
        f"<p style='margin:6px 0 0;font-size:14px;color:#a0a0b8;'>{date_str}</p>"
        "</td></tr>"
    )

    footer = (
        "<tr><td style='background-color:#f9f9fb;padding:20px 40px;"
        "border-top:1px solid #eeeeee;'>"
        "<p style='margin:0;font-size:12px;color:#999999;text-align:center;'>"
        f"You received this email because you are subscribed to {config.DIGEST_NAME}."
        "</p></td></tr></table></td></tr></table></body></html>"
    )

    parts = [header]

    for section in sections:
        section_title = section['title']
        items = section['items']

        # Section header
        parts.append(
            "<tr><td style='padding:28px 40px 0;'>"
            f"<h2 style='margin:0 0 4px;font-size:13px;font-weight:700;"
            f"text-transform:uppercase;letter-spacing:1.2px;color:#6c63ff;'>"
            f"{section_title}</h2>"
            "<hr style='border:none;border-top:2px solid #6c63ff;"
            "margin:0 0 20px;width:40px;' align='left' />"
            "</td></tr>"
        )

        for i, item in enumerate(items):
            clean_desc = _clean_description(
                item.get('description', ''), item.get('title', '')
            )
            is_first = i == 0
            is_last = i == len(items) - 1
            padding = '0 40px 20px' if is_first else ('20px 40px 28px' if is_last else '20px 40px')

            parts.append(
                f"<tr><td style='padding:{padding};'>"
                f"<p style='margin:0 0 4px;font-size:12px;font-weight:600;"
                f"text-transform:uppercase;letter-spacing:0.5px;color:#999999;'>"
                f"{item.get('source', '')}</p>"
                f"<a href='{item.get('link', '#')}' style='font-size:17px;"
                f"font-weight:700;color:#1a1a2e;text-decoration:none;"
                f"line-height:1.3;'>{item.get('title', '')}</a>"
                f"<p style='margin:8px 0 0;font-size:14px;line-height:1.6;"
                f"color:#555555;'>{clean_desc}</p>"
                "</td></tr>"
            )

            if not is_last:
                parts.append(
                    "<tr><td style='padding:0 40px;'>"
                    "<hr style='border:none;border-top:1px solid #eeeeee;"
                    "margin:0;' /></td></tr>"
                )

    parts.append(footer)
    return "".join(parts)


def _clean_description(text: str, title: str) -> str:
    """Helper function to clean the description text

    Args:
        text (str): The text to clean
        title (str): The title of the article

    Returns:
        str: The cleaned text
    """
    separators = [title, '[…]', '...Keep reading', '(...)']
    for sep in separators:
        if sep in text:
            # Split and take the part before the separator
            text = text.split(sep, 1)[0]
    return text.strip()


# --- Helper function to send the email ---
def _send_smtp_email(subject: str, text_body: str, html_body: str, sender: str, recipient: str):
    """Constructs and sends a multipart email via SMTP.

    Args:
        subject (str): The email subject
        text_body (str): The plain text email body
        html_body (str): The HTML email body
        sender (str): The sender's email address
        recipient (str): The recipient's email address

    Returns:
        None
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


# noinspection PyUnusedLocal
@bp.timer_trigger(
    schedule=config.DIGESTS_NCRON,
    arg_name="digest_timer",
    run_on_startup=False
)
def digest_email(digest_timer: func.TimerRequest) -> None:
    """
    Timer trigger to fetch news digests and send them via email.

    Args:
        digest_timer (func.TimerRequest): The timer request object.

    Returns:
        None
    """
    try:
        with requests.Session() as session:
            session.params = {'api-key': config.KEY}
            response = session.get(f"{config.ENDPOINT}emails")
            response.raise_for_status()
            categories = response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Can't get list of emails from RSS endpoint: {e}")
        return

    logging.info(f"Retrieved {len(categories)} categories to process.")

    # Group categories by recipient so each person gets one combined email
    recipient_sections: Dict[str, List[dict]] = defaultdict(list)

    for category in categories:
        title = category['title']
        nid = category['id']
        recipient = category['email']

        try:
            response = requests.get(
                f"{config.ENDPOINT}items/{nid}", params={'api-key': config.KEY}
            )
            response.raise_for_status()
            items = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Can't retrieve items for '{title}': {e}")
            continue

        if not items:
            logging.info(f"No new items for '{title}'. Skipping.")
            continue

        logging.info(f"Retrieved {len(items)} new items for '{title}'.")
        recipient_sections[recipient].append({'title': title, 'items': items})

    # Send one email per recipient with all their sections
    for recipient, sections in recipient_sections.items():
        date_str = datetime.now().strftime('%B %d, %Y')
        full_subject = config.DIGEST_NAME

        # Plain text fallback
        text_parts = [f"{full_subject}\n\n"]
        for section in sections:
            text_parts.append(f"--- {section['title']} ---\n\n")
            for item in section['items']:
                text_parts.append(
                    f"{item.get('created', '')}\n"
                    f"{item.get('source', '')}\n"
                    f"{item.get('title', '')}\n"
                    f"{item.get('link', '')}\n\n"
                )
        text_body = "".join(text_parts)

        html_body = _build_html_email(full_subject, date_str, sections)

        try:
            _send_smtp_email(full_subject, text_body, html_body, config.SENDER, recipient)
            logging.info(f"Successfully sent digest email to {recipient}.")
        except Exception as e:
            logging.error(f"Unable to send digest email to {recipient}: {e}")
