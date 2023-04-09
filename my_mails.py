"""Import modules"""
import os
from typing import Union

import smtplib
import ssl
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

import pandas as pd

from log_sett import logger, contextualize_class_logs
from config_handler import config_vars


@contextualize_class_logs(tag='report')
class MailSMTP:
    """
    A class for handling SMTP connections.

    This class manages the connection to the SMTP server, providing context manager
    support for connection management.
    """

    sender: str = config_vars['mail']['sender']
    password: str = config_vars['mail']['password']
    smtp_server: str = config_vars['mail']['smtp_server']
    port: Union[int, str] = config_vars['mail']['port_server']

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self) -> None:
        """Connect to the SMTP server."""
        logger.info('Navazuji připojení k poštovnímu serveru')
        try:
            self.connection = smtplib.SMTP_SSL(
                self.smtp_server, self.port, context=ssl.create_default_context())
            self.connection.login(self.sender, self.password)
        except smtplib.SMTPAuthenticationError:
            logger.error('Připojení se nepodařilo navázat!')
            sys.exit(1)
        else:
            logger.info('Připojení navázáno')

    def disconnect(self) -> None:
        """Close the connection to the SMTP server."""
        self.connection.quit()
        logger.info('Připojení ukončeno')


@contextualize_class_logs(tag='report')
class _CommonMessageFunctionality:
    """
    A base class for providing common email message functionality.

    This class provides methods to handle attachments, and to convert a dataset
    to an HTML table. It should be subclassed by classes that require these functionalities.
    """

    def __init__(self) -> None:
        self.recipients: list = []
        self.message = MIMEMultipart()

    def _attach(self, attachments: list) -> None:
        """Method that allows you to create attachments"""

        logger.info('Zpracovávám přílohu')
        for file in attachments:
            try:
                file_path = os.path.join(config_vars['directories']['TEMP'], file)
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    f'attachment; filename={file}')
                    self.message.attach(part)
                    logger.info(f'Příloha {file} -> OK')
            except FileNotFoundError:
                logger.warning(f'Příloha {file} -> NENALEZENO')

    def data2html(self, dataset: list, columns: list) -> str:
        """Convert dataset into HTML table"""

        # Create header of HTML table
        data_frame = pd.DataFrame(dataset, columns=columns)
        # Start indexation from `1`
        data_frame.index = data_frame.index + 1
        # Using Pandas make HTML table from dataset
        html_table = data_frame.to_html(
            classes='', justify='left', index=True, index_names=['№'])
        # Name index columnt as `№`
        html_table = html_table.replace('<th></th>', '<th>№</th>')
        # Load template from TXT file and add HTML table
        file_path = os.path.join(config_vars['directories']['templates'],
                                 config_vars['files']['report_feed'])
        with open(file_path, 'r', encoding='utf-8') as template:
            main_html: str = template.read().format(table=html_table)

        return main_html


@contextualize_class_logs(tag='report')
class ReminderOverdue(_CommonMessageFunctionality):
    """
    A class for sending reminder emails about overdue invoices.

    Inherits from the _CommonMessageFunctionality class to use the common email
    message features. Provides methods for setting up and sending reminder emails
    with appropriate details and attachments.
    """

    def __init__(self, mail_smtp: MailSMTP) -> None:
        self.mail_smtp: MailSMTP = mail_smtp
        self.currency: str = ''
        self.amount: str = ''
        self.invoices_in_msg: str = ''
        self.body: str = ''

    def _set_details(self, recipient: str, currency: str, amount: str, invoices: list) -> None:
        """Method preparing message details"""

        # Uncomment coed below to switch recipient (for debugging purpose)
        # recipient = config_vars['mail']['support']
        self.recipients: list = recipient.replace(' ', '').replace(';', ',').split(',')
        self.amount: str = str(amount).replace('.', ',')
        self.invoices_in_msg: str = ', '.join(str(invoice) for invoice in invoices)
        subjects_langs: dict = {
            'CZK': 'FRPNEU: Upomínka faktury po splatnosti',
            'EUR': 'FRPNEU: Reminder of overdue invoices'
        }
        subject: str = subjects_langs.get(currency, 'FLEKC s.r.o.')

        # Set body
        if currency == 'CZK':
            file_path = os.path.join(config_vars['directories']['templates'],
                                     config_vars['files']['overdue_czk'])
            with open(file_path, 'r', encoding='utf-8') as czk_body:
                self.body = czk_body.read().format(self.invoices_in_msg, self.amount)
        elif currency == 'EUR':
            file_path = os.path.join(config_vars['directories']['templates'],
                                     config_vars['files']['overdue_eur'])
            with open(file_path, 'r', encoding='utf-8') as eur_body:
                self.body = eur_body.read().format(self.invoices_in_msg, self.amount)

        self.message = MIMEMultipart()
        self.message["From"] = self.mail_smtp.sender
        self.message["Date"] = formatdate(localtime=True)
        self.message["To"]: str = ', '.join(self.recipients)
        self.message["Subject"]: str = subject
        self._attach(invoices)
        self.message.attach(MIMEText(self.body, "plain"))

    def send_message(self, recipient: str, currency: str, amount: str, invoices: list) -> None:
        """Send message method"""

        logger.info(f'Připravuji zprávu příjemci {recipient}')
        self._set_details(recipient, currency, amount, invoices)
        self.mail_smtp.connection.sendmail(self.mail_smtp.sender, self.recipients, self.message.as_string())
        logger.info('Odesláno!')


@contextualize_class_logs(tag='report')
class DailyFrFeed(_CommonMessageFunctionality):
    """
    A class for sending daily orders reports as emails.

    Inherits from the _CommonMessageFunctionality class to use the common email
    message features. Provides methods for setting up and sending daily orders
    report emails with appropriate details and attachments.
    """

    def __init__(self, mail_smtp: MailSMTP) -> None:
        self.mail_smtp = mail_smtp
        self.message = MIMEMultipart()
        self.invoices: list = []
        self.body = ''

    def _set_details(self, recipient: str, details: list) -> None:
        """Method preparing message details"""

        # Uncomment coed below to switch recipient (for debugging purpose)
        # recipient = config_vars['mail']['support']
        self.recipients = recipient.replace(' ', '').replace(';', ',').split(',')
        columns = ['Order No', 'Invoce', 'Amount', 'Parcels', 'Carrier', 'Tracking']
        self.body = self.data2html(details, columns)

        # Make list of invoices
        self.invoices.clear()
        self.invoices = [row[1] for row in details]

        # Set email details
        self.message = MIMEMultipart()
        self.message["From"] = self.mail_smtp.sender
        self.message["Date"] = formatdate(localtime=True)
        self.message["To"] = ', '.join(self.recipients)
        self.message["Subject"] = 'FRPNEU: Daily orders report'
        self._attach(self.invoices)
        self.message.attach(MIMEText(self.body, "html"))

    def send_message(self, recipient: str, body_details: list) -> None:
        """Send message method"""

        logger.info(f'Připravuji zprávu příjemci {recipient}')
        self._set_details(recipient, body_details)
        self.mail_smtp.connection.sendmail(self.mail_smtp.sender, self.recipients, self.message.as_string())
        logger.info('Odesláno!')


def send_supervisor_report(supervisor):
    """
    Sends a supervisor report email using an existing SMTP connection.

    Parameters:
    -----------
    supervisor : str
        A string containing one or multiple supervisor email addresses, separated by semicolons or commas.
    """

    logger.info(f'Připravuji report pro {supervisor}')

    recipients = supervisor.replace(' ', '').replace(';', ',').split(',')
    with open('report.log', 'r', encoding='UTF-8') as f:
        body = f.read()
    
    with MailSMTP() as mail_smtp:
        message = MIMEMultipart()
        message["From"] = mail_smtp.sender
        message["Date"] = formatdate(localtime=True)
        message["To"] = ', '.join(recipients)
        message["Subject"] = 'MailRobot: report'
        message.attach(MIMEText(body, "plain"))
        mail_smtp.connection.sendmail(mail_smtp.sender, recipients, message.as_string())
    
    logger.info('Report odeslán!')
