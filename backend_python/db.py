import os
from sqlmodel import Field, Session, SQLModel, create_engine
from typing import Annotated, Optional
from fastapi import Depends


class Occupancy(SQLModel, table=True):
    id: str = Field(primary_key=True)
    occupancy: str
    project: str
    tag: str
    name: str
    position: str

    
class Projects(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    description: str
    instructions: str
    project_name: str
    sensor_configuration: str
    image: str


postgres_url = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"

engine = create_engine(postgres_url, connect_args={})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

