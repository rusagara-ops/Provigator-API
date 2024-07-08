from fastapi import FastAPI, Path, Depends, HTTPException
from typing import Optional, List, Dict
from models import Client, UpdateClient, UserSchema, UserLoginSchema, Project, UpdateProject
# from app.auth.jwt_handler import signJWT, decodeJWT
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID, uuid4
# from app.auth.jwt_bearer import JwtBearer

app = FastAPI()

clients_db: Dict[int, Client] = {}
projects_db: Dict[int, Project] = {}

users_db = {}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@app.post("/register", tags=["User"])
def user_signup(user: UserSchema):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    users_db[user.email] = {
        "fullname": user.fullname,
        "email": user.email,
        "password": user.password
    }
    return {"message": "User created successfully"}

@app.post("/user/login", tags=["User"])
def user_login(user: UserLoginSchema):
    if user.email not in users_db or users_db[user.email]["password"] != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    access_token = signJWT(user.email)
    return {"access_token": access_token}

def verify_token(token: str = Depends(oauth2_scheme)):
    payload = decodeJWT(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = users_db[payload]
    return user

@app.post("/api/v1/clients", tags=["Clients"])
def create_client(client: Client):
    client_id = len(clients_db) + 1
    clients_db[client_id] = client
    return {"id": client_id, "client": client}

@app.patch("/api/v1/clients/{id}", tags=["Clients"])
def update_client(id: int, client: UpdateClient):
    if id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, value in client.dict(exclude_unset=True).items():
        setattr(clients_db[id], key, value)
    return clients_db[id]

@app.get("/api/v1/clients", tags=["Clients"])
def list_clients():
    return clients_db

@app.get("/api/v1/clients/{id}", tags=["Clients"])
def get_client(id: int):
    if id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    return clients_db[id]

@app.delete("/api/v1/clients/{id}", tags=["Clients"])
def delete_client(id: int):
    if id not in clients_db:
        raise HTTPException(status_code=404, detail="Client not found")
    del clients_db[id]
    return {"message": "Client deleted"}


@app.post("/api/v1/projects", tags=["Projects"])
def create_project(project: Project):
    project_id = len(projects_db) + 1
    projects_db[project_id] = project
    return {"id": project_id, "project": project}

@app.patch("/api/v1/projects/{id}", tags=["Projects"])
def update_project(id: int, project: UpdateProject):
    if id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict(exclude_unset=True).items():
        setattr(projects_db[id], key, value)
    return projects_db[id]

@app.get("/api/v1/projects", tags=["Projects"])
def list_projects():
    return projects_db

@app.get("/api/v1/projects/{id}", tags=["Projects"])
def get_project(id: int):
    if id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[id]

@app.delete("/api/v1/projects/{id}", tags=["Projects"])
def delete_project(id: int):
    if id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[id]
    return {"message": "Project deleted"}

