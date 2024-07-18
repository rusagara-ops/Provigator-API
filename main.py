from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from models import Client, UpdateClient, UserSchema, Project, UpdateProject
from fastapi.security import OAuth2PasswordBearer
from auth.google_auth import oauth
from database import execute, fetch
import os
from dotenv import load_dotenv
from typing import Optional
import requests

load_dotenv()

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

origins = [
    "https://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initializing database
@app.on_event("startup")
async def startup():
    await execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL
    )
    """)
    await execute("""
    CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pm_names TEXT NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        thumbnail TEXT NOT NULL,
        client TEXT NOT NULL,
        type TEXT NOT NULL,
        url TEXT NOT NULL,
        bug_report_url TEXT NOT NULL
    )
    """)
    await execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        fullname TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Google Authentication Endpoints
@app.get("/api/v1/auth/signup", tags=["Authentication"])
async def google_signup(request: Request):
    redirect_uri = "http://localhost:8000/api/v1/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/v1/auth/login", tags=["Authentication"])
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/api/v1/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/v1/auth/callback", tags=["Authentication"])
async def google_callback(request: Request):
    try:
        response = requests.post("https://accounts.google.com/o/oauth2/token", data={
            "code": request.query_params["code"],
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": "http://localhost:8000/api/v1/auth/callback",
            "grant_type": "authorization_code"
        })
        access_token = response.json().get("access_token")
        user_info = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
        user_data = user_info.json()
        user_email = user_data.get("email")
        user_fullname = user_data.get("name")

        existing_user = await fetch("SELECT * FROM users WHERE email = ?", (user_email,))
        if not existing_user:
            await execute(query="INSERT INTO users (email, fullname, password) VALUES (?, ?, ?)", is_many=False, args=(user_email, user_fullname, ""))
        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Authentication failed")

# User Management Endpoints
@app.post("/api/v1/users", tags=["User"])
async def create_user(user: UserSchema):
    existing_user = await fetch("SELECT * FROM users WHERE email = ?", (user.email,))
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    query = "INSERT INTO users (email, fullname, password) VALUES (?, ?, ?)"
    await execute(query=query, is_many=False, args=[user.email, user.fullname, user.password])
    return {"message": "User created successfully"}

@app.patch("/api/v1/users/{email}", tags=["User"])
async def update_user(email: str, user_update: UserSchema):
    existing_user = await fetch("SELECT * FROM users WHERE email = ?", (email,))
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        query = f"UPDATE users SET {key} = ? WHERE email = ?"
        await execute(query=query, is_many=False, args=[value, email])

    return {"message": "User updated successfully"}

@app.delete("/api/v1/users/{email}", tags=["User"])
async def delete_user(email: str):
    existing_user = await fetch("SELECT * FROM users WHERE email = ?", (email,))
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    await execute(query="DELETE FROM users WHERE email = ?", args=[email])
    return {"message": "User deleted successfully"}

@app.get("/api/v1/users", tags=["User"])
async def list_users(page: int = Query(1, ge=1), limit: int = Query(10, ge=1), q: Optional[str] = None):
    offset = (page - 1) * limit
    if q:
        query = "SELECT email, fullname FROM users WHERE fullname LIKE ? OR email LIKE ? LIMIT ? OFFSET ?"
        raw_users = await fetch(query, (f"%{q}%", f"%{q}%", limit, offset))
    else:
        query = "SELECT email, fullname FROM users LIMIT ? OFFSET ?"
        raw_users = await fetch(query, (limit, offset))

    users = [{"email": email, "name": fullname} for email, fullname in raw_users]
    return users

# Client Management Endpoints
@app.post("/api/v1/clients", tags=["Clients"])
async def create_client(client: Client):
    existing_client = await fetch("SELECT * FROM clients WHERE name = ? AND country = ?", (client.name, client.country))
    if existing_client:
        raise HTTPException(status_code=400, detail="Client already exists")
    query = "INSERT INTO clients (name, country) VALUES (?, ?)"
    await execute(query=query, is_many=False, args=[client.name, client.country])
    return {"message": "Client created successfully"}

@app.patch("/api/v1/clients/{id}", tags=["Clients"])
async def update_client(id: int, client: UpdateClient):
    existing_client = await fetch("SELECT * FROM clients WHERE id = ?", args=[id])
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        query = f"UPDATE clients SET {key} = ? WHERE id = ?"
        await execute(query=query, is_many=False, args=[value, id])

    return {"message": "Client updated successfully"}

@app.get("/api/v1/clients", tags=["Clients"])
async def list_clients(page: int = Query(1, ge=1), limit: int = Query(10, ge=1), q: Optional[str] = None):
    offset = (page - 1) * limit
    if q:
        query = "SELECT id, name, country FROM clients WHERE name LIKE ? OR country LIKE ? LIMIT ? OFFSET ?"
        raw_clients = await fetch(query, (f"%{q}%", f"%{q}%", limit, offset))
    else:
        query = "SELECT id, name, country FROM clients LIMIT ? OFFSET ?"
        raw_clients = await fetch(query, (limit, offset))

    clients = [{"id": id, "name": name, "country": country} for id, name, country in raw_clients]
    return clients

@app.get("/api/v1/clients/{id}", tags=["Clients"])
async def get_client(id: int):
    existing_client = await fetch("SELECT * FROM clients WHERE id = ?", args=[id])
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return existing_client[0]

@app.delete("/api/v1/clients/{id}", tags=["Clients"])
async def delete_client(id: int):
    existing_client = await fetch("SELECT * FROM clients WHERE id = ?", args=[id])
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    await execute(query="DELETE FROM clients WHERE id = ?", args=[id])
    return {"message": "Client deleted successfully"}

# Project Management Endpoints
@app.post("/api/v1/projects", tags=["Projects"])
async def create_project(project: Project):
    existing_project = await fetch("SELECT * FROM projects WHERE name = ? AND client = ?", (project.name, project.client))
    if existing_project:
        raise HTTPException(status_code=400, detail="Project already exists")
    query = """
    INSERT INTO projects (pm_names, name, description, thumbnail, client, type, url, bug_report_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    await execute(query=query, is_many=False, args=[project.pm_names, project.name, project.description, project.thumbnail, project.client, project.type, project.url, project.bug_report_url])
    return {"message": "Project created successfully"}

@app.patch("/api/v1/projects/{id}", tags=["Projects"])
async def update_project(id: int, project: UpdateProject):
    existing_project = await fetch("SELECT * FROM projects WHERE id = ?", args=[id])
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)
    for key, value in update_data.items():
        query = f"UPDATE projects SET {key} = ? WHERE id = ?"
        await execute(query=query, is_many=False, args=[value, id])

    return {"message": "Project updated successfully"}

@app.get("/api/v1/projects", tags=["Projects"])
async def list_projects(page: int = Query(1, ge=1), limit: int = Query(10, ge=1), q: Optional[str] = None):
    offset = (page - 1) * limit
    if q:
        query = "SELECT id, pm_names, name, description, thumbnail, client, type, url, bug_report_url FROM projects WHERE name LIKE ? OR pm_names LIKE ? LIMIT ? OFFSET ?"
        raw_projects = await fetch(query, (f"%{q}%", f"%{q}%", limit, offset))
    else:
        query = "SELECT id, pm_names, name, description, thumbnail, client, type, url, bug_report_url FROM projects LIMIT ? OFFSET ?"
        raw_projects = await fetch(query, (limit, offset))

    projects = [{
        "id": id,
        "pm_names": pm_names,
        "name": name,
        "description": description,
        "thumbnail": thumbnail,
        "client": client,
        "type": type,
        "url": url,
        "bug_report_url": bug_report_url
    } for id, pm_names, name, description, thumbnail, client, type, url, bug_report_url in raw_projects]
    return projects

@app.get("/api/v1/projects/{id}", tags=["Projects"])
async def get_project(id: int):
    project = await fetch("SELECT * FROM projects WHERE id = ?", args=[id])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project[0]

@app.delete("/api/v1/projects/{id}", tags=["Projects"])
async def delete_project(id: int):
    existing_project = await fetch("SELECT * FROM projects WHERE id = ?", args=[id])
    if not existing_project:
        raise HTTPException(status_code=404, detail="Project not found")
    await execute(query="DELETE FROM projects WHERE id = ?", args=[id])
    return {"message": "Project deleted successfully"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
