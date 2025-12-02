import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from gspread.exceptions import WorksheetNotFound

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.metadata.readonly"
]

flow = InstalledAppFlow.from_client_secrets_file(
    r"C:\Users\SRI RAM JANJANAM\Downloads\private.json",
    SCOPES
)
creds = flow.run_local_server(port=0)
gc = gspread.authorize(creds)

drive_service = build('drive', 'v3', credentials=creds)

results = drive_service.files().list(
    q="mimeType='application/vnd.google-apps.spreadsheet'",
    pageSize=100,
    fields="files(id, name)"
).execute()

files = results.get('files', [])

if not files:
    print("No Google Sheets found in your Drive.")
    exit()

print("Google Sheets in your Drive:")
for idx, file in enumerate(files, start=1):
    print(f"{idx}. {file['name']} (ID: {file['id']})")

sheet_idx = int(input("\nEnter the number of the spreadsheet you want to use: "))
spreadsheet = gc.open_by_key(files[sheet_idx - 1]['id'])

sheet_names = [sheet.title for sheet in spreadsheet.worksheets()]
print("\nAvailable sheet/tab names:")
for idx, name in enumerate(sheet_names, start=1):
    print(f"{idx}. {name}")

tab_idx = int(input("\nEnter the number of the sheet/tab to insert data into: "))

try:
    sheet = spreadsheet.worksheet(sheet_names[tab_idx - 1])
except WorksheetNotFound:
    sheet_name = input("Sheet not found. Enter new sheet name to create: ")
    sheet = spreadsheet.add_worksheet(title=sheet_name, rows="100", cols="20")

data_to_insert = ["Sri Ram", "Python Insert", "Working!"]  # customize your data
sheet.append_row(data_to_insert)

print(f"\nData inserted successfully into '{sheet.title}' in '{spreadsheet.title}'!")
