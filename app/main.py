from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def home():
    return {"message": "IT Helpdesk is running!"}
