"""
MIT License

Copyright (c) 2023 Eduard Pisarev <hello@pishon.store>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os
import traceback
import sys
from log_sett import logger
from maintenance import get_filenames, init_maintenance
from config_handler import config_vars, SCRIPT_DIR
import CRM
import raw2order
import datetime
import my_mails
from my_mails import MailSMTP, send_supervisor_report


# Check if the script was run correctly
if len(sys.argv) != 2:
    raise SystemExit("Usage: python script.py <argument>")

logger.info('Program started')

# What argument is being used
ARGUMENT = sys.argv[1]
# ARGUMENT: str = 'overdue'

# import dicts with settings
dirs: dict = config_vars['directories']
files: dict = config_vars['files']

# Maintenance
init_maintenance()

# Start main program depending on mode (arguement)
def main():
    """Main function of the program"""

    if ARGUMENT == 'frfeed':
        logger.info(f'Argument: {ARGUMENT}')

        # Get list of invoices, clients etc.
        query_path: str = os.path.join(SCRIPT_DIR, dirs['templates'], files['select_frfeed'])
        raw_data: list = CRM.select_data(query_path)

        # Check if there is something to process
        if not raw_data:
            logger.info('No data in CRM to process')
            raise SystemExit("No data in CRM to process")

        # Download invoices from list but only invoice numbers that are not already downloaded
        logger.info('Collecting data to download')
        dl_data = [row[:3] for row in raw_data if row[1] not in get_filenames(dirs['TEMP'])]
        if len(dl_data) > 0:
            CRM.download(dl_data)
        else:
            logger.info('Nothing new to download')

        # Sort and group raw data into structured dictionary
        logger.info('Sort and group raw dataset')
        mail_dict: dict = raw2order.prepare_frfeed(raw_data)

        # Unpack data from dictionary and send email
        with logger.contextualize(tag='report'):
            logger.info(f'Preparing {len(mail_dict)} emails')
            logger.info(f'At {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        with MailSMTP() as mail_smtp:
            for i, (email, details) in enumerate(mail_dict.items(), 1):
                with logger.contextualize(tag='report'):
                    logger.info(f'Processing email №{i}')
                m = my_mails.DailyFrFeed(mail_smtp)
                m.send_message(email, details)

        # Send content of 'report.log' to supervisor
        supervisor = config_vars['mail']['frfeed_sup']
        send_supervisor_report(supervisor)


    elif ARGUMENT == 'overdue':
        logger.info(f'Argument: {ARGUMENT}')

        # Get list of invoices, clients etc.
        query_path: str = os.path.join(SCRIPT_DIR, dirs['templates'], files['select_ovedue'])
        raw_data: list = CRM.select_data(query_path)

        # Check if there is something to process
        if not raw_data:
            logger.info('No data in CRM to process')
            raise SystemExit("No data in CRM to process")

        # Download invoices from list but only invoice numbers that are not already downloaded
        logger.info('Preparing to download invoices')
        dl_data = [row[:3] for row in raw_data if row[1] not in get_filenames(dirs['TEMP'])]
        if len(dl_data) > 0:
            CRM.download(dl_data)
        else:
            logger.info('Nothing to download')

        # Sort and group raw data into structured dictionary
        logger.info('Sort and group raw dataset')
        mail_dict: dict = raw2order.prepare_overdue(raw_data)

        # Unpack data from dictionary and send email
        with logger.contextualize(tag='report'):
            logger.info(f'Preparing emails to send at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        email_count = 0
        with MailSMTP() as mail_smtp:
            for currency, details in mail_dict.items():
                for email, inv_data in details.items():
                    email_count += 1
                    with logger.contextualize(tag='report'):
                        logger.info(f'Zpracovávám email №{email_count}')
                    overdue_mail = my_mails.ReminderOverdue(mail_smtp)
                    overdue_mail.send_message(email, currency, inv_data['total_amount'], inv_data['invoices'])

        # Send content of 'report.log' to supervisor
        supervisor = config_vars['mail']['overdue_sup']
        send_supervisor_report(supervisor)


    else:
        # Handle invalid argument values
        logger.error(f'Invalid argument: {ARGUMENT}')


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("An unexpected error occurred:")
        exc_info = sys.exc_info()
        tb_str = "".join(traceback.format_exception(*exc_info))
        logger.error("Traceback: \n" + tb_str)
        sys.exit(1)
