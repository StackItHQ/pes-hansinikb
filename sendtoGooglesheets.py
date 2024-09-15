import mysql.connector
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

'''
Data from MySQL
'''
def fetch_mysql_data():
    cnx = mysql.connector.connect(user='root', password='lock97keyT$2024', host='localhost', database='book')
    cursor = cnx.cursor()

    # Query to fetch data from MySQL
    query = "SELECT * FROM recipe"
    cursor.execute(query)
    data = cursor.fetchall()

    cursor.close()
    cnx.close()

    # Define a header row
    header = ['id', 'average_rating', 'cooking_time', 'difficulty_level', 'instructions', 'title']
    # Combine the header and the data
    formatted_data = [header] + [list(row) for row in data]

    return formatted_data

'''
Get data from Google Sheets
'''
def fetch_sheets_data():
    # Load service account credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = "D:\\Placements\\superjoin\\pes-hansinikb\\service key\\superjoinhansini-55e147f53218.json"
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # The ID of your spreadsheet
    SPREADSHEET_ID = '13DTl_NPT4i_u-zDhLuND-Wy6yDnDW0_jQRe3sv3XPeE'
    RANGE_NAME = 'Sheet1!A1:F'

    # Fetch data from Google Sheets
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get('values', [])

    # Convert all string values to their proper types for comparison
    for row in values[1:]:  # Skip header row
        row[0] = int(row[0])  # 'id'
        row[1] = float(row[1])  # 'average_rating'
        row[2] = int(row[2])  # 'cooking_time'

    return values

'''
Write data to Google Sheets
'''
def write_to_sheets(data):
    # Load service account credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = "D:\\Placements\\superjoin\\pes-hansinikb\\service key\\superjoinhansini-55e147f53218.json"
    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # The ID of your spreadsheet
    SPREADSHEET_ID = '13DTl_NPT4i_u-zDhLuND-Wy6yDnDW0_jQRe3sv3XPeE'
    RANGE_NAME = 'Sheet1!A1'

    # Write data to Google Sheets
    body = {
        'values': data
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
        valueInputOption='RAW', body=body).execute()

    print('{0} cells updated.'.format(result.get('updatedCells')))

'''
Write data to MySQL
'''
def write_to_mysql(data):
    cnx = mysql.connector.connect(user='root', password='lock97keyT$2024', host='localhost', database='book')
    cursor = cnx.cursor()

    # Iterate over each row and update or insert into MySQL
    for row in data[1:]:  # Skip header row
        id_val = row[0]
        cursor.execute("SELECT * FROM recipe WHERE id = %s", (id_val,))
        existing_row = cursor.fetchone()

        if existing_row:
            # Update the row if it exists
            update_query = """
            UPDATE recipe 
            SET average_rating = %s, cooking_time = %s, difficulty_level = %s, instructions = %s, title = %s 
            WHERE id = %s
            """
            cursor.execute(update_query, (row[1], row[2], row[3], row[4], row[5], id_val))
        else:
            # Insert a new row if it doesn't exist
            insert_query = """
            INSERT INTO recipe (id, average_rating, cooking_time, difficulty_level, instructions, title) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (row[0], row[1], row[2], row[3], row[4], row[5]))

    cnx.commit()
    cursor.close()
    cnx.close()

'''
Main logic: Compare Google Sheets and MySQL data, then sync accordingly
'''
def sync_sheets_and_database():
    mysql_data = fetch_mysql_data()  # Get data from MySQL
    sheets_data = fetch_sheets_data()  # Get data from Google Sheets

    print("sheets_data", sheets_data)
    print("mysql_data", mysql_data)

    # Compare the two datasets
    if mysql_data == sheets_data:
        print("Data is consistent. Writing latest MySQL data to Google Sheets.")
        write_to_sheets(mysql_data)  # Data matches, write MySQL data to Google Sheets
    else:
        print("Data is inconsistent. Writing Google Sheets data to MySQL.")
        write_to_mysql(sheets_data)  # Data doesn't match, write Google Sheets data to MySQL

# Run the sync
sync_sheets_and_database()
