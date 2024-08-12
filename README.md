# Provigator API

## Overview

Provigator is a RESTful API built with FastAPI, designed to serve as the central hub for managing projects within Awesomity Lab. This internal tool allows team members to upload projects, conduct thorough testing, and report any bugs or issues. By providing a streamlined process for bug tracking and project management, Provigator ensures that all projects meet quality standards before being delivered to clients.

## Project Background

During my internship at Awesomity Lab, I was responsible for developing the backend of Provigator. The project aimed to help the company track bugs across all their projects. Every team member could upload their project to Provigator and collaborate with others to identify and fix issues. This API was a crucial component in enhancing the company's software quality assurance process, making Provigator the go-to platform for internal project testing and bug reporting.

## Technologies Used

- **Framework**: FastAPI
- **Programming Language**: Python
- **Database**: SQLite
- **Deployment**: Internal company network

## Features

### 1. **Client Management**
   - **Create a New Client**: `POST /api/v1/clients`
   - **Update a Client by ID**: `PATCH /api/v1/clients/{id}`
   - **List All Clients**: `GET /api/v1/clients`
   - **Get a Client by ID**: `GET /api/v1/clients/{id}`
   - **Delete a Client by ID**: `DELETE /api/v1/clients/{id}`

### 2. **Project Management**
   - **Create a New Project**: `POST /api/v1/projects`
   - **Update a Project by ID**: `PATCH /api/v1/projects/{id}`
   - **List All Projects**: `GET /api/v1/projects`
   - **Get a Project by ID**: `GET /api/v1/projects/{id}`
   - **Delete a Project by ID**: `DELETE /api/v1/projects/{id}`

### 3. **User Management**
   - **Signup with Google**: `POST /api/v1/auth/signup`
   - **Login with Google**: `POST /api/v1/auth/login`
   - **Update a User by ID**: `PATCH /api/v1/users/{id}`
   - **Delete a User by ID**: `DELETE /api/v1/users/{id}`
   - **List All Users**: `GET /api/v1/users`

### 4. **Advanced Features**
   - **Pagination**:
     - Paginate Users: `GET /api/v1/users?page={page}&limit={limit}`
     - Paginate Projects: `GET /api/v1/projects?page={page}&limit={limit}`
     - Paginate Clients: `GET /api/v1/clients?page={page}&limit={limit}`
   - **Searching**:
     - Search Users: `GET /api/v1/users?q={search_term}`
     - Search Projects: `GET /api/v1/projects?q={search_term}`
     - Search Clients: `GET /api/v1/clients?q={search_term}`

## Database Schema

The API interacts with a SQLite database to manage the following entities:

1. **Users**: Information about the users who have access to Provigator, including their roles.
2. **Projects**: Details about the projects managed within the company, including URLs for bug reporting.
3. **Clients**: Information on the clients associated with the projects.

