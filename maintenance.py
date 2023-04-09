"""Module for maintanance purpose."""
import os
import datetime
import sys
from config_handler import config_vars
from log_sett import logger, report_log


def get_filenames(directory: str) -> list:
    """Create list of all PDF files inside given directory."""

    dir_path = os.path.join(os.getcwd(), directory)
    return [os.path.splitext(f)[0] for f in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, f))
            and f.lower().endswith('.pdf')]


def remove_old_invoices(directory: str, file_age_days: int) -> None:
    """
    Remove PDF files from the specified directory that are older than the given number of days.
    """

    deleted_count = 0
    for file in os.listdir(directory):
        if os.path.splitext(file)[1] == ".pdf":
            file_path = os.path.join(directory, file)
            created_time = datetime.datetime.fromtimestamp(
                os.path.getctime(file_path))
            if (datetime.datetime.now() - created_time).days > file_age_days:
                try:
                    os.remove(file_path)
                    logger.info(f'Deleted {file_path}')
                    deleted_count += 1
                except (OSError, PermissionError):
                    logger.error('Error while deleting files')
    if deleted_count != 0:
        logger.info(f'Deleted {deleted_count} files for maintanence purpose.')


def clear_report_log() -> None:
    """Cleaning report.log file in root directory when program starts"""

    if not os.path.exists(report_log):
        # Create the file "report.log" if it doesn't exist
        with open(report_log, 'w', encoding='utf-8'):
            logger.info(f'Created file {report_log}')
            # pass
    else:
        # Open the file in write mode to truncate the content
        with open(report_log, 'w', encoding='utf-8'):
            logger.info(f'Cleaning file {report_log}')
            # pass


def _check_dirs(dirs: list) -> bool:
    for directory in dirs:
        if os.path.isdir(directory):
            logger.info(f'Directory: {directory} -> OK')
        else:
            logger.warning(f'Directory: {directory} -> MISSING')
            try:
                logger.info(f'Trying to create directory {directory}')
                os.makedirs(directory)
            except PermissionError:
                logger.error('Failed!')
                return False
            logger.info(f'Directory: {directory} Succesfuly created! -> OK')

    return True


def _check_templates(files: list) -> bool:
    templ_dir = config_vars['directories']['templates']
    missing_files = []
    for file in files:
        logger.info(f'File: {file} -> OK')
        path = os.path.join(templ_dir, file)
        if not os.path.isfile(path):
            logger.info(f'File: {file} -> MISSING')
            missing_files.append(file)

    if missing_files:
        logger.error(f'Missing important files: {", ".join(missing_files)}')
        return False

    return True


def check_environment(dirs: list, files: list) -> bool:
    """
    Method check if all necessary files and directories are even created.

    Function will try to create necessary directories but 
    the files should be created manually.
    The `files` means templates of messages and database queries or even `conf.ini` file.
    """
    if not _check_dirs(dirs) or not _check_templates(files):
        logger.error('Exiting program!')
        sys.exit(1)


def init_maintenance() -> None:
    """
    Initialize function

    Functions:
    - check_environment
    - remove_old_invoices
    - clear_main_log
    """

    logger.info("Initializing maintenance")

    clear_report_log()

    conf_directories = list(config_vars['directories'].values())
    conf_files = list(config_vars['files'].values())

    check_environment(dirs=conf_directories, files=conf_files)
    remove_old_invoices(config_vars['directories']['TEMP'], 30)
