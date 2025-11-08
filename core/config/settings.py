from datetime import date, datetime
from pathlib import Path

from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CLIENT_DIR = BASE_DIR / 'setup'

# Database connection parameters
DATABASE = {
    'SERVER': str(config('DB_SERVER', default=' ', cast=str)),
    'DATABASE': str(config('DB_DATABASE', default=' ', cast=str)),
    'SCHEMA': str(config('DB_SCHEMA', default=' ', cast=str)),
    'USERNAME': str(config('DB_USERNAME', default=' ', cast=str)),
    'PASSWORD': str(config('DB_PASSWORD', default=' ', cast=str)),
    'DRIVER': str(config('DB_DRIVER', default='ODBC Driver 17 for SQL Server', cast=str)),
    'TRUSTED_CONNECTION': config('DB_TRUSTED_CONNECTION', default='no', cast=str),
}

DATABASE_URL = (
    f'mssql+pyodbc://{DATABASE["USERNAME"]}:{DATABASE["PASSWORD"]}@{DATABASE["SERVER"]}/{DATABASE["DATABASE"]}'
    f'?driver={DATABASE["DRIVER"]}'
)

DB_COLLATION = str(config('DB_COLLATION', default='Latin1_General_BIN2', cast=str))

# Debug mode
DEBUG = config('DEBUG', default=True, cast=bool)

# API connection parameters
SERVER_BASE_ADDRESS = str(config('SERVER_BASE_ADDRESS', default=' ', cast=str))

API_USER = str(config('API_USER', default=' ', cast=str))
API_PASSWORD = str(config('API_PASSWORD', default=' ', cast=str))

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
    'EMAIL_USER': str(config('EMAIL_USER', default=' ', cast=str)),
    'USER': str(config('SMTP_USER', default=' ', cast=str)),
    'PASSWORD': str(config('EMAIL_PASSWORD', default=' ', cast=str)),
    'HOST': str(config('EMAIL_HOST', default='smtp.gmail.com', cast=str)),
    'PORT': config('EMAIL_PORT', default=465, cast=int),
}

# Email recipient for error notifications
# email_user = str(EMAIL_CONFIG.get('EMAIL_USER'))

# if email_user and email_user.strip():
#     config_emails = Generics().load_config_yaml()

#     EMAIL_RECIPIENTS = config_emails.get('send_to', [])
#     EMAIL_COPIES = config_emails.get('send_cc', [])

# Schedule settings
SCHEDULING = {
    'ENABLED': config('SCHEDULE_ENABLED', default=True, cast=bool),
    # Timetable for scheduling
    'START_TIME': config('SCHEDULE_START_TIME', default='08:00', cast=str),
    'END_TIME': config('SCHEDULE_END_TIME', default='18:00', cast=str),
    # Execution interval in minutes
    'INTERVAL_MINUTES': config('SCHEDULE_INTERVAL_MINUTES', default=60, cast=int),
}

# Namespaces definitions (essential for CIUS-PT)
# These are the default namespaces for UBL 2.1
NS_CBC = 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
NS_CAC = 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
NS_ROOT = 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2'
NSMAP = {
    'ubl': NS_ROOT,
    'cac': NS_CAC,
    'cbc': NS_CBC,
}
NS_ESPAP = 'urn:cen.eu:en16931:2017#compliant#urn:feap.gov.pt:CIUS-PT:2.0.0'

# Directory to save generated XML files
XML_DIRECTORY = str(config('OUTPUT_DIRECTORY', default='output', cast=str))

if XML_DIRECTORY is not None:
    OUTPUT_DIRECTORY = BASE_DIR / XML_DIRECTORY

if not Path(OUTPUT_DIRECTORY).exists():
    Path(OUTPUT_DIRECTORY).mkdir(parents=True, exist_ok=True)

# Other settings
CLEANUP_FILENAMES = ('-', '_')  # Characters to clean from filenames
CUSTOMER_PROFILE = str(config('CUSTOMER_PROFILE', default='DEFAULT', cast=str))
