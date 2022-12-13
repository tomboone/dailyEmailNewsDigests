import logging
import json
import sys
import requests
import settings
from datetime import datetime
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def lambda_handler(event, context):
    # Prep logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # API credentials
    endpoint = settings.endpoint
    key = settings.key

    # Get list of emails
    email_ep = 'emails'

    try:
        response = requests.get(endpoint + email_ep + '?api-key=' + key)
        response.raise_for_status()
    except Exception as e:
        logger.error('Can\'t get list of emails from rss endpoint: {}'.format(e))
        sys.exit()

    emails = json.loads(response.text)

    logger.info('Retrieved {} emails'.format(len(emails)))

    for email in emails:
        subject = email['title']
        nid = email['id']
        recipient = email['email']

        message = MIMEMultipart("alternative")
        message["Subject"] = subject + ' News Digest: ' + datetime.now().strftime('%m/%d/%Y')
        message["From"] = settings.sender
        message["To"] = recipient

        # Start email text
        text = """\
{}

""".format(message['subject'])

        html = """\
<html>
    <body>
        <h1>{}</h1>
        <hr style=\"margin-bottom:1em\" />
""".format(message['subject'])

        item_ep = 'items/'

        try:
            response = requests.get(endpoint + item_ep + nid + '?api-key=' + key)
            response.raise_for_status()
        except Exception as e:
            logger.error('Can\'t retrieve items for {} email: {}'.format(subject, e))
            continue

        items = json.loads(response.text)

        # Check if there are new items. If not, skip email
        if len(items) == 0:
            print('No items for {} email today'.format(subject))
            continue

        logger.info('Retrieved {} new items for {} email'.format(len(items), subject))

        for item in items:
            description = item['description']

            sep = item['title']
            description = description.split(sep, 1)[0]

            sep = '[…]'
            description = description.split(sep, 1)[0]

            sep = '...Keep reading'
            description = description.split(sep, 1)[0]

            sep = '(...)'
            description = description.split(sep, 1)[0]

            text += """\
{}
{}
{}
{}

""".format(item['created'], item['source'], item['title'], item['link'])

            html += """\
        <h3 style=\"margin:0 0 0.5em;font-size:1em\">{}</h3>
        <h2 style=\"margin:0;font-size:1.25em\"><a href=\"{}\">{}</a></h2>
        <p>{}</p>
        <hr style=\"margin-bottom:1em\" />
""".format(item['source'], item['link'], item['title'], description)

        html += """\
    </body>
<html>"""

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        # The email client will try to render the last part first
        message.attach(part1)
        message.attach(part2)

        # Create secure connection with server and send email
        context = ssl.create_default_context()
        try:
            with smtplib.SMTP("smtp.fastmail.com", port=587) as server:
                server.starttls(context=context)
                server.login(settings.smtp_user, settings.smtp_pwd)
                server.sendmail(
                    settings.sender, recipient, message.as_string()
                )
        except Exception as e:
            logger.error('Unable to send {} email: {}'.format(subject, e))
            continue

        logger.info('Sent {} email'.format(subject))
