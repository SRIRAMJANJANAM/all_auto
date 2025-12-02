import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from gspread.exceptions import WorksheetNotFound


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

flow = InstalledAppFlow.from_client_secrets_file(
    r"C:\Users\SRI RAM JANJANAM\Downloads\private.json",
    SCOPES
)

creds = flow.run_local_server(port=0)
client = gspread.authorize(creds)

spreadsheet = client.open_by_url(
    "https://docs.google.com/spreadsheets/d/1XaE3PloavxpffFkBC3siubYoH75ot743Vi7Kz0mVnMo"
)

sheet_name = "simple" 
try:
    sheet = spreadsheet.worksheet(sheet_name)
except WorksheetNotFound:
    print(f"Sheet '{sheet_name}' not found. Creating new sheet.")
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")
 
sheet.append_row(["Sri Ram", "Python Insert", "Working!"])

print(f"Inserted into sheet '{sheet_name}'!")
