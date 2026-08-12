
🚧 Currently under development.


# IT Helpdesk System
A full-stack IT Helpdesk System built with Python and FastAPI.

Users (Two types)
Employee
Support Staff

Employee can:
Log in
View dashboard
Create support ticket
View own tickets
View ticket details
Add comments
Close their ticket

Support Staff can:
Log in
View all tickets
View ticket details
Change ticket status
Change priority
Assign tickets
Add resolution notes


## installation
python -m venv venv
venv\Scripts\activate

main:
pip install fastapi uvicorn jinja2 python-multipart
pip install "pwdlib[argon2]"
pip install email-validator

later:
pip install itsdangerous

## Run
python -m uvicorn app.main:app --reload

## Technology stack

Backend
    Python
    FastAPI
    SQLite

Frontend
    HTML5
    CSS3
    JavaScript
    Jinja2

Testing
    pytest
    FastAPI TestClient

Development
    VS Code
    Git
    GitHub
    GitHub Copilot



## features
Registration
Login
SQLite user table
Session middleware
user_id stored in session
Email stored in session
Protected dashboard
Logout
Login error message
Register link
User account checking


## Registration Validation
Email is required and validated.
backend email validation.
Duplicate emails are rejected.
Password must be 8+ characters.
Requires uppercase, lowercase, and number.
Password confirmation must match.
Passwords are securely hashed before storage.
Protected dashboard using authenticated session.
User ID and email are stored in the session after login.
Server uses the session to identify the logged-in user.
Users without a valid session are redirected to the login page.
Logout clears the session.