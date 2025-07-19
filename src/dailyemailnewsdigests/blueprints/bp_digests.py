""" Blueprint for retrieving and sending dailyemailnewsdigests """
import logging
import requests
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import azure.functions as func

import src.dailyemailnewsdigests.config as config

bp: func.Blueprint = func.Blueprint()


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
        # Use a session for potentially better performance with multiple requests
        with requests.Session() as session:
            session.params = {'api-key': config.KEY}
            response = session.get(f"{config.ENDPOINT}emails")
            response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
            emails = response.json()
    except requests.exceptions.RequestException as e:
        # Catching a more specific exception is better
        logging.error(f"Can't get list of emails from RSS endpoint: {e}")
        return  # Use return instead of sys.exit()

    logging.info(f"Retrieved {len(emails)} emails to process.")

    for email in emails:
        subject = email['title']
        nid = email['id']
        recipient = email['email']
        full_subject = f"{subject} News Digest: {datetime.now().strftime('%m/%d/%Y')}"

        try:
            response = requests.get(f"{config.ENDPOINT}items/{nid}", params={'api-key': config.KEY})
            response.raise_for_status()
            items = response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Can't retrieve items for '{subject}' email: {e}")
            continue  # Skip to the next email

        if not items:
            logging.info(f"No new items for '{subject}' email today. Skipping.")
            continue

        logging.info(f"Retrieved {len(items)} new items for '{subject}' email.")

        # Build email content efficiently
        text_parts = [f"{full_subject}\n\n"]
        html_parts = []

        for item in items:
            clean_desc = _clean_description(item.get('description', ''), item.get('title', ''))

            text_parts.append(
                f"{item.get('created', '')}\n"
                f"{item.get('source', '')}\n"
                f"{item.get('title', '')}\n"
                f"{item.get('link', '')}\n\n"
            )
            html_parts.append(
                f"<h3 style='margin:0 0 0.5em;font-size:1em'>{item.get('source', '')}</h3>"
                f"<h2 style='margin:0;font-size:1.25em'>"
                f"<a href='{item.get('link', '#')}'>{item.get('title', '')}</a>"
                f"</h2>"
                f"<p>{clean_desc}</p>"
                f"<hr style='margin-bottom:1em' />"
            )

        # Assemble the final email body
        text_body = "".join(text_parts)
        html_body = (
            f"<html><body><h1>{full_subject}</h1>"
            f"<hr style='margin-bottom:1em' />{''.join(html_parts)}"
            f"</body></html>"
        )

        try:
            _send_smtp_email(full_subject, text_body, html_body, config.SENDER, recipient)
            logging.info(f"Successfully sent '{subject}' email to {recipient}.")
        except Exception as e:
            logging.error(f"Unable to send '{subject}' email: {e}")
            continue
