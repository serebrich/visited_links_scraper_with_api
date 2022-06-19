import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_TAB = 'links'
GOOGLE_SHEET_LINK = os.getenv('GOOGLE_SHEET_LINK')
GOOGLE_SHEET_USE_COLUMNS = [0, 1]
GOOGLE_API_SCOPE = ['https://www.googleapis.com/auth/spreadsheets']
GOOGLE_SECRET_KEY_FILENAME = os.getenv('GOOGLE_SECRET_KEY_FILENAME')

LOGGER_FORMAT = "{time} - {level} - {message}"
LOGGER_ROTATING = "1 day"

ENTRY_DATE_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

THREADS_COUNT = PARALLEL_CONNECTIONS = 20
CONNECTION_POOL_SIZE = 500
REQUESTS_RETRIES_COUNT = 3
TIME_BETWEEN_RETRIES = 0.1
REQUESTS_TIMEOUT = 15
DEFAULT_HEADERS = {'Accept': '*/*',
                   'Connection': 'keep-alive',
                   'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/51.0.2704.103 Safari/537.36,',
                   'Cache-Control': 'max-age=0'}

DATABASE_URL = os.getenv('POSTGRES_CREDS')
