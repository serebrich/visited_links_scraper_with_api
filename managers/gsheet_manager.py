from oauth2client.service_account import ServiceAccountCredentials
import gspread_dataframe as gd
import gspread
from loguru import logger
import pandas as pd
import os
import config


class GoogleSheetManager:
    def __init__(self):
        self.google_client = self.google_auth()

    @staticmethod
    def google_auth() -> gspread.Client:
        """
        Creating connecting with Google API
        :return: google client obj
        """
        try:
            scope = config.GOOGLE_API_SCOPE
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             config.GOOGLE_SECRET_KEY_FILENAME), scope
            )
            client = gspread.authorize(creds)
            return client
        except Exception:
            logger.exception("Can't create connection with Google API")

    def get_google_worksheet(self, sheet_url: str, tab_name: str) -> gspread.worksheet:
        """
        Get Google Sheet object
        :param sheet_url: str
        :param tab_name: str
        :return: gspread.worksheet
        """
        try:
            wsh = self.google_client.open_by_url(sheet_url).worksheet(tab_name)
            return wsh
        except Exception:
            logger.exception('Cant get google worksheet object')

    def get_google_sheet_data(self, sheet_url: str, tab_name: str, columns: list = None) -> pd.DataFrame:
        """
        Getting data from Google Sheet and make pd.DataFrame from it
        :param columns: list
        :param tab_name: str
        :param sheet_url: str
        :return: pd.DataFrame
        """
        try:
            worksheet = self.get_google_worksheet(sheet_url, tab_name)
            df = gd.get_as_dataframe(worksheet, usecols=columns)
            if df.empty:
                logger.info('DataFrame is Empty')
            df.drop_duplicates(inplace=True)
            df.dropna(inplace=True)
            logger.success(f'Get DataFrame successfully: {len(df)} rows')
            return df
        except Exception:
            logger.exception('Cant get gshet data')
            return pd.DataFrame()
