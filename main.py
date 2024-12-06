from fastapi import FastAPI, Form, Request, status, Depends
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pyodbc
import uvicorn
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Azure AD details for authentication
tenant_id = "your-tenant-id"
client_id = "your-client-id" 
client_secret = "your-client-secret"
server_name = "your-server-name.database.windows.net"  # Your Azure SQL Server name
database_name = "your-database-name"  # Your Azure SQL Database name

# MSAL authority and resource
authority = f"https://login.microsoftonline.com/{tenant_id}"
resource = "https://database.windows.net/"

# Initialize the FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# MSAL Authentication to get access token for Azure SQL Database
def get_access_token():
    app = msal.ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )
    token_response = app.acquire_token_for_client(scopes=[resource + "/.default"])

    if "access_token" in token_response:
        return token_response["access_token"]
    else:
        raise Exception("Failed to acquire access token")

def get_db_connection():
    # Get the Azure AD access token using MSAL
    access_token = get_access_token()

    # Correct ODBC connection string for Azure AD authentication
    conn_str = (
        f"Driver={{ODBC Driver 17 for SQL Server}};"
        f"Server=tcp:{server_name},1433;"
        f"Database={database_name};"
        "Authentication=ActiveDirectoryServicePrincipal;"
        f"AccessToken={access_token}"  # Use the AccessToken here, not User/Password
    )

    conn = pyodbc.connect(conn_str)
    return conn
    

# Replace the function to query the database for both the list of monsters and their details
def get_monsters_from_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM Monsters")
        monsters = [row['name'] for row in cursor.fetchall()]
    finally:
        conn.close()
    return monsters

def get_monster_details_from_db(name: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Assuming you have a 'Monsters' table that also stores monster details (e.g., description, stats)
        cursor.execute("SELECT * FROM Monsters WHERE name = ?", (name,))
        monster = cursor.fetchone()
        if monster:
            return {
                "name": monster['name'],
                "description": monster['description'],  # Example fields
                "abilities": monster['abilities'],      # Example fields
                # Add other fields here if needed
            }
        return None
    finally:
        conn.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        return templates.TemplateResponse('hello.html', {"request": request, 'name': name})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

@app.get("/monsters", response_class=HTMLResponse)
async def get_monsters(request: Request):
    try:
        monsters = get_monsters_from_db()  # Fetch the list of monsters from the database
    except Exception as e:
        print(f"Database query failed: {e}")
        monsters = []
    return templates.TemplateResponse('monsters.html', {"request": request, "monsters": monsters})

@app.get("/monsters/{name}", response_class=HTMLResponse)
async def get_monster_details(request: Request, name: str):
    try:
        monster = get_monster_details_from_db(name)  # Fetch monster details from the database
        if monster:
            return templates.TemplateResponse('monster_details.html', {"request": request, "monster": monster})
        else:
            return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"Database query failed: {e}")
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080)
