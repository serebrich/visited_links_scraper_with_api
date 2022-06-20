import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import (ConnectionError, SSLError, ChunkedEncodingError,
                                 Timeout, TooManyRedirects, InvalidURL)
from multiprocessing.dummy import Pool as ThreadPool
from loguru import logger
from tld import get_tld
from typing import List, Union
from datetime import datetime
from bs4 import BeautifulSoup
try:
    from config import *
    from managers.gsheet_manager import GoogleSheetManager
except ImportError:
    import sys
    sys.path.append('../')
    from config import *
    from managers.gsheet_manager import GoogleSheetManager

logger.add("../logs/scraping.log", format=LOGGER_FORMAT, rotation=LOGGER_ROTATING, catch=True)


class Scraper(GoogleSheetManager):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=CONNECTION_POOL_SIZE,
                                                pool_connections=PARALLEL_CONNECTIONS)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def make_request(self, url: str) -> Union[Response, None]:
        """
        Make request to url
        :param url: str
        :return: requests.Response obj | None
        """
        try:
            response = self.session.get(url, timeout=REQUESTS_TIMEOUT,
                                        headers=DEFAULT_HEADERS, allow_redirects=True)
            return response
        except SSLError:
            logger.error(f"Cant make request to {url} ||SSL error")
        except ConnectionError:
            logger.error(f"Cant make request to {url} ||Connection error")
        except Timeout:
            logger.error(f"Cant make request to {url} ||Timeout error")
        except TooManyRedirects:
            logger.error(f"Cant make request to {url} ||Too Many Redirects error")
        except InvalidURL:
            logger.error(f"Cant make request to {url} || Not Valid URL")
        except ChunkedEncodingError:
            logger.error(f"Cant make request to {url} || Chunked Encoding Error")
        except Exception:
            logger.exception(f"Cant make request to {url} || Non-excepted Error")

    @staticmethod
    def get_title_from_html(url: str, html: str) -> Union[str, None]:
        """
        Parse html and get title
        :param url: str
        :param html: str
        :return: str
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            title = soup.title
            if not title:
                logger.info(f"Is no title on {url}")
                return ''
            return title.text.strip()
        except Exception:
            logger.exception(f"Cant get title from {url}")

    def parse_response(self, response: Response, url_visited: dict) -> dict:
        """
        Parse response and make result dict
        :param response: requests.Response
        :param url_visited: dict
        :return: dict
        """
        url_info = {
            'url': url_visited['URL'],
            'visit_datetime': None,
            'redirect_to': None,
            'status_code': None,
            'title': None,
            'domain': None,
            'scrap_datetime': datetime.now(),
            'error': None,
        }

        try:
            url_info['visit_datetime'] = datetime.strptime(url_visited['Datetime'], ENTRY_DATE_DATETIME_FORMAT)
        except ValueError:
            logger.error(f"Cant convert data to datetime obj :: {url_visited['Datetime']}")

        if response is not None:
            if response.status_code == 200:
                try:
                    url_info['status_code'] = response.status_code
                    url_info['redirect_to'] = response.url if response.url != url_visited['URL'] else None
                    url_info['title'] = self.get_title_from_html(url_visited['URL'], response.text)
                    url_info['domain'] = get_tld(response.url, as_object=True).parsed_url.hostname
                    url_info['error'] = False
                    logger.success(f"Success request to {url_visited['URL']}")
                except Exception:
                    logger.exception(f"Cant parse success response :: {url_visited['URL']}")
                    return url_info
            else:
                try:
                    url_info['status_code'] = response.status_code
                    url_info['domain'] = get_tld(url_visited['URL'], as_object=True).parsed_url.hostname
                    url_info['error'] = True
                    logger.error(f"Unsuccessful request to {url_visited['URL']}, status {response.status_code}")
                except Exception:
                    logger.exception(f"Cant parse unsuccessful response :: {url_visited['URL']}")
                    return url_info
        else:
            url_info['error'] = True

        return url_info

    def grab_info_from_url(self, url_visited: dict) -> dict:
        """
        Make request ti url and parse it
        :param url_visited: dict: {'URL': str, 'Datetime': str}
        :return: dict
        """
        response = self.make_request(url_visited['URL'])
        result = self.parse_response(response, url_visited)

        return result

    def run(self) -> Union[List[dict], None]:
        """
        Main function for scrap URLs from Google Sheets
        :return: list or None: [{}, {}] | None
        """
        pool = None
        results = None

        entry_data_df = self.get_google_sheet_data(GOOGLE_SHEET_LINK, GOOGLE_SHEET_TAB, GOOGLE_SHEET_USE_COLUMNS)
        if entry_data_df.empty:
            return None

        try:
            pool = ThreadPool(THREADS_COUNT)
            results = pool.map(self.grab_info_from_url, entry_data_df.to_dict('records'))
        finally:
            if pool:
                pool.close()

        return results
