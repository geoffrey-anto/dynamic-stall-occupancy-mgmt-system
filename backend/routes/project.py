from fastapi import APIRouter
from db import SessionDep
from sqlmodel import select
from db import Project

project_router = APIRouter()


@project_router.post("/create")
def create_new_project():
    # Run ml pipeline to create a new project
    # Save the project to the database
    return {"status": "ok"}


@project_router.get("/list/")
def list_projects(session: SessionDep):
    projects = session.execute(select(Project)).all()
    result = []
    for project in projects:
        result.append(project[0])
    return result


@project_router.get("/list/{project_id}")
def list_projects_by_id(project_id: int, session: SessionDep):
    projects = session.execute(select(Project).where(Project.id == project_id)).all()
    result = []
    for project in projects:
        result.append(project[0])
    return result
