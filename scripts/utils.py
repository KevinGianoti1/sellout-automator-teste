
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

def carregar_curva_abc(secrets):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
    client = gspread.authorize(creds)
    url = "https://docs.google.com/spreadsheets/d/1YXjBruX8jb90HOWy07Ccwn1oC846g_AnNnbyIh3HquU/edit?usp=sharing"
    sheet = client.open_by_url(url).sheet1
    data = sheet.get_all_records()
    return pd.DataFrame(data)
