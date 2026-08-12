from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import create_user, get_connection, create_user_table, get_user, create_test_user
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from app.auth import secure_hash, verify_password
from pydantic import EmailStr


app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="secret-key-will-move-to-env"
)


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

    if not user:
      return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid email or password."}
    )

    password_hash = user[2]
    if not verify_password(password, password_hash):
        return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid email or password."}
        )

    # create login session here 
    request.session["user_id"] = user[0]
    request.session["email"] = user[1]
   
    return RedirectResponse(
        url="/dashboard",
        status_code=303
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
    email: EmailStr = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)):

    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error": "Passwords do not match."}
        )

    existing_user = get_user(email)

    if (len(password) < 8 
    or not any(char.isdigit() for char in password) 
    or not any(char.isupper() for char in password)
    or not any(char.islower() for char in password)):
        return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={
            "error": "Password must be at least 8 characters and contain an uppercase letter, lowercase letter, and number."
        })

    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Email already registered."})
    
    password_hash = secure_hash(password)
    created_at = datetime.now().isoformat()

    create_user(email, password_hash,created_at)
    return RedirectResponse(
        url="/",
        status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    if "user_id" not in request.session:
        return RedirectResponse( url="/", status_code=303)
    email = request.session.get("email")

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"email": email})


@app.get("/tickets", response_class=HTMLResponse)
async def tickets(request: Request):

    if "user_id" not in request.session:
        return RedirectResponse( url="/", status_code=303)
    email = request.session.get("email")

    return templates.TemplateResponse(
        request=request,
        name="ticket.html",
        context={"email": email})


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):

    if "user_id" not in request.session:
           return RedirectResponse( url="/", status_code=303)
    email = request.session.get("email")
   
    return templates.TemplateResponse(
           request=request,
           name="profile.html",
           context={"email": email})

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(
        url="/",
        status_code=303)