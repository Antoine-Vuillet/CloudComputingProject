from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import uvicorn

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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

def get_monsters_from_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name FROM Monsters"))
        monsters = [row['name'] for row in result]
    return monsters

@app.get("/monsters", response_class=HTMLResponse)
async def get_monsters(request: Request):
    try:
        monsters = get_monsters_from_db()
    except Exception as e:
        print(f"Database query failed: {e}")
        monsters = []
    return templates.TemplateResponse('monsters.html', {"request": request, "monsters": monsters})


@app.get("/monsters/autocomplete")
async def autocomplete(query: str):
    url = 'https://www.dnd5eapi.co/api/monsters/'
    response = requests.get(url)

    if response.status_code == 200:
        monsters_data = response.json()
        monster_names = [
            monster['name'] for monster in monsters_data['results']
            if query.lower() in monster['name'].lower()
        ]
        return {"suggestions": monster_names}
    return {"suggestions": []}
@app.post('/monsters', response_class=HTMLResponse)
async def get_monster_details(request: Request, name: str = Form(...)):
    # Replace spaces with hyphens and remove special characters for the API call
    formatted_name = name.lower().replace(" ", "-").replace("(", "").replace(")", "")
    url = f'https://www.dnd5eapi.co/api/monsters/{formatted_name}/'
    response = requests.get(url)

    if response.status_code == 200:
        monster_data = response.json()
        return templates.TemplateResponse('monster_details.html', {"request": request, "monster": monster_data})
    else:
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8080)


