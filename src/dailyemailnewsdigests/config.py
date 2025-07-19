""" Configurations for dailyemailnewsdigests """
import os
import logging

DIGESTS_NCRON: str = os.environ.get("DIGESTS_NCRON", "0 0 10 * * *")
ENDPOINT: str = os.getenv('ENDPOINT')
KEY: str = os.getenv('KEY')

SENDER: str = os.getenv('SENDER')
SMTP_SERVER: str = os.getenv('SMTP_SERVER')
SMTP_USER: str = os.getenv('SMTP_USER')
SMTP_PWD: str = os.getenv('SMTP_PWD')
SMTP_PORT: int = int(os.getenv('SMTP_PORT', '587'))
