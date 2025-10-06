from datetime import date, datetime
from pathlib import Path

from decouple import config
from utils.generics import Generics

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CLIENT_DIR = BASE_DIR / 'setup'

# Database connection parameters
DATABASE = {
    'SERVER': config('DB_SERVER', default=' ', cast=str),
    'DATABASE': config('DB_DATABASE', default=' ', cast=str),
    'SCHEMA': config('DB_SCHEMA', default=' ', cast=str),
    'USERNAME': config('DB_USERNAME', default=' ', cast=str),
    'PASSWORD': config('DB_PASSWORD', default=' ', cast=str),
    'DRIVER': config('DB_DRIVER', default='ODBC Driver 17 for SQL Server', cast=str),
    'TRUSTED_CONNECTION': config('DB_TRUSTED_CONNECTION', default='no', cast=str),
}

DB_COLLATION = str(config('DB_COLLATION', default='Latin1_General_BIN2', cast=str))

# Debug mode
DEBUG = config('DEBUG', default=True, cast=bool)

# API connection parameters
API = {
    'BASE_URL': config('BASE_URL', default=' ', cast=str),
    'APP_KEY': config('APP_KEY', default=' ', cast=str),
    'APP_SECRET': config('APP_SECRET', default=' ', cast=str),
}

# Logging configuration
LOG_DIR = 'logs'
LOG_ROOT_LEVEL = 'DEBUG'
LOG_CONSOLE_LEVEL = 'INFO'
LOG_INFO_FILE_ENABLED = True
LOG_INFO_FILENAME = 'app_info.log'
LOG_INFO_FILE_LEVEL = 'INFO'
LOG_ERROR_FILE_ENABLED = True
LOG_ERROR_FILENAME = 'app_error.log'
LOG_ERROR_FILE_LEVEL = 'ERROR'
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# Sage X3 database table settings
DEFAULT_LEGACY_DATE = date(1753, 1, 1)
DEFAULT_LEGACY_DATETIME = datetime(1753, 1, 1)
DAYS_TO_SEARCH = config('DAYS_TO_SEARCH', default=30, cast=int)

# Email configuration
EMAIL_CONFIG = {
    'EMAIL_USER': config('EMAIL_USER', default=' ', cast=str),
    'USER': config('SMTP_USER', default=' ', cast=str),
    'PASSWORD': config('EMAIL_PASSWORD', default=' ', cast=str),
    'HOST': config('EMAIL_HOST', default='smtp.gmail.com', cast=str),
    'PORT': config('EMAIL_PORT', default=465, cast=int),
}

# Email recipient for error notifications
email_user = str(EMAIL_CONFIG.get('EMAIL_USER'))

if email_user and email_user.strip():
    config_emails = Generics().load_config_yaml()

    EMAIL_RECIPIENTS = config_emails.get('send_to', [])
    EMAIL_COPIES = config_emails.get('send_cc', [])
