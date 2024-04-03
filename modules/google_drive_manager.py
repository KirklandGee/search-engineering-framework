import pandas as pd
import gspread
import requests
from bs4 import BeautifulSoup
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleSheetsManager(object):
  
    def __init__(self, sheet_name: str):
        self.credentials_file_path = "credentials/credentials.json"
        self.gc = gspread.service_account(filename=self.credentials_file_path)
        self.sheet = self.gc.open(sheet_name)
        self.worksheet = self.sheet.get_worksheet(0)
        self.values = self.worksheet.get_all_values()

    def get_worksheet(self): 
        return self.worksheet

    def set_worksheet(self, worksheet_name: str):
        self.worksheet = self.sheet.worksheet(worksheet_name) 

    def get_all_values(self):
        values = self.worksheet.get_all_values()
        self.values = values
    
    def create_dataframe(self, worksheet_name=None) -> object:

        if worksheet_name:
            self.set_worksheet(worksheet_name)
            
        dataframe = pd.DataFrame(self.worksheet.get_all_records())

        return dataframe
    
    def write_dataframe_to_sheets(self, dataframe, worksheet_name=None) -> None:

        if worksheet_name:
            self.set_worksheet(worksheet_name)
            self.worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())
        else:
            self.worksheet.update([dataframe.columns.values.tolist()] + dataframe.values.tolist())

    def fetch_and_write_h1_tags(self, url_column_name: str, read_worksheet: str, write_worksheet: str) -> None:
        df = self.create_dataframe_from_google_sheet(read_worksheet)
        h1_tags = []
        for url in df[url_column_name]:
            try:
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                h1_tag = soup.find('h1').get_text(strip=True) if soup.find('h1') else "No H1 Tag Found"
                h1_tags.append([url, h1_tag])
            except Exception as e:
                h1_tags.append([url, f"Error: {e}"])
                
        h1_df = pd.DataFrame(h1_tags, columns=[url_column_name, 'H1 Tag'])
        self.write_dataframe_to_sheets(write_worksheet, h1_df)        