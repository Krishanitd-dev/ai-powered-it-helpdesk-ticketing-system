from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import create_user, get_connection, create_user_table, get_user, create_test_user




app = FastAPI()
create_user_table()
create_test_user()

# HTML
templates = Jinja2Templates(directory="./app/templates")

# CSS/ JavaScript
app.mount("/static", StaticFiles(directory="./app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.post("/login")
async def login(request:Request,
    email: str = Form(...),
    password: str = Form(...)
):
    user = get_user(email)

    if user is None or user [2] !=password:
      return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid email or password."}
    )
   
    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):

    existing_user = get_user(email)

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "An account with this email already exists."
            }
        )

    create_user(email, password)

    return RedirectResponse(
        url="/",
        status_code=303
    )