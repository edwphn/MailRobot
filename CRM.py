import os
import requests
import time
import pyodbc
import sys
from typing import List
from log_sett import logger
from config_handler import config_vars, SCRIPT_DIR


class DownloadError(Exception):
    pass

class DatabaseConnectionError(Exception):
    pass


def download(data: list) -> None:
    """
    This function checks a list to see if there is anything to
    download, and calls download functions for items such as `pdf_invoice`.
    """

    logger.info(f'About to download {len(data)} files: {", ".join(num[1] for num in data)}')
    try:
        pdf_invoice(data)
    except (requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.RequestException) as exc:
        raise DownloadError(f'An error occurred while downloading invoices: {exc}')
    else:
        time.sleep(10)
        logger.info('Completed!')


def pdf_invoice(data: List[str]) -> None:
    """Function generates XML request (string) and sending it to API using `requests` module."""

    currency_map: dict = {'CZK': 190, 'EUR': 3052}

    start_static_part = f"""<?xml version="1.0" encoding="Windows-1250"?>
    <dat:dataPack version="2.0" id="01" ico="{config_vars['api']['ico']}"
    application="Tisk" note="XML tisk z programu Pohoda" 
    xmlns:dat="http://www.stormware.cz/schema/version_2/data.xsd" 
    xmlns:prn="http://www.stormware.cz/schema/version_2/print.xsd" 
    xmlns:ftr="http://www.stormware.cz/schema/version_2/filter.xsd">"""
    main_part = ''
    end_static_part = """\n</dat:dataPack>"""

    for no, (bd_id, invoice, currency) in enumerate(data, 1):
        abs_invoice_path: str = os.path.join(
            SCRIPT_DIR,
            config_vars['directories']['TEMP'],
            invoice + '.pdf'
        )
        tmp = f"""
        <dat:dataPackItem version="2.0" id="00{no}">
            <prn:print version="1.0">
                <prn:record agenda="vydane_faktury">
                    <ftr:filter>
                        <ftr:id>{bd_id}</ftr:id>
                    </ftr:filter>
                </prn:record>
                <prn:printerSettings>
                    <prn:report>
                        <prn:id>{currency_map[currency]}</prn:id>
                    </prn:report>
                    <prn:pdf>
                        <prn:fileName>{abs_invoice_path}</prn:fileName>
                    </prn:pdf>
                </prn:printerSettings>
            </prn:print>
        </dat:dataPackItem>"""
        main_part += tmp

    request_body = start_static_part + main_part + end_static_part
    headers = {config_vars['api']['api_key_auth']: config_vars['api']['api_value_auth']}

    try:
        logger.info('Sending XML request to API')
        logger.info('Request is being processed.')
        request = requests.post(config_vars['api']['api_url'], data=request_body.encode(
            'windows-1250'), headers=headers, timeout=900)

    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.RequestException) as e:
        logger.error(f'API connection error: {e}')
        sys.exit(1)

    else:
        if request.status_code == 200:
            logger.info('API processed request!')
        else:
            logger.error(f'API: Status code not 200 ({request.status_code}). Exiting...')
            sys.exit(1)


def select_data(select_query: str) -> list:
    """Select data from database"""

    try:
        connection = pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            f'SERVER={config_vars["db"]["db_server"]};'
            f'DATABASE={config_vars["db"]["db_name"]};'
            f'UID={config_vars["db"]["db_user"]};'
            f'PWD={config_vars["db"]["db_password"]}'
        )

    except pyodbc.Error:
        raise DatabaseConnectionError('Error connecting to the database')

    with open(select_query, 'r', encoding='utf-8') as query:
        sql = query.read()

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    return list(rows)
