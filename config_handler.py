"""
config_handler.py

Provides functions to read and parse configuration settings from an INI file.

Functions:
    - read_config_file(file_path: str) -> configparser.ConfigParser
    - get_config_vars(config: configparser.ConfigParser) -> dict[str, dict[str, Any]]
"""
import configparser
import os
import sys
from typing import Any, Dict


# Script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Config file
CONFIG_FILE = 'config.ini'

# Check if config file exists
if not os.path.exists(CONFIG_FILE):
    print(f"Configuration file '{CONFIG_FILE}' not found.")
    sys.exit(1)

try:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

except (FileExistsError, TypeError) as e:
    print(f"Error reading configuration file: {e}")
    sys.exit(1)

# Set up variables from config
try:
    config_vars: Dict[str, Dict[str, Any]] = {
        'directories': {
            'TEMP': config['directories']['dir_temp'],
            'templates': config['directories']['templates_dir']
        },
        'files': {
            'report_feed': config['files']['report_feed'],
            'overdue_czk': config['files']['overdue_czk'],
            'overdue_eur': config['files']['overdue_eur'],
            'select_frfeed': config['files']['select_frfeed'],
            'select_ovedue': config['files']['select_ovedue']
        },
        'db': {
            'db_server': config['db']['DB_SERVER'],
            'db_name': config['db']['DB_NAME'],
            'db_user': config['db']['DB_USER'],
            'db_password': config['db']['DB_PASSWORD']
        },
        'api': {
            'api_url': config['api']['URL'],
            'api_key_auth': config['api']['AUTH_KEY'],
            'api_value_auth': config['api']['AUTH_VALUE'],
            'ico': config['api']['ICO']
        },
        'mail': {
            'sender': config['mail']['Sender'],
            'password': config['mail']['Pass'],
            'smtp_server': config['mail']['SmtpServer'],
            'port_server': config['mail']['PortServer'],
            'overdue_sup': config['mail']['OverdueSupervisor'],
            'frfeed_sup': config['mail']['FrFeedSupervisor'],
            'support': config['mail']['Support']
        }
    }

except KeyError as e:
    raise Exception(f"Error setting configuration variables: {e}")
