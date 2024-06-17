from dataclasses import field

from pydantic import BaseModel


class Actor(BaseModel):
    id: str
    name: str


class Writer(BaseModel):
    id: str
    name: str


class Director(BaseModel):
    id: str
    name: str


class Filmwork(BaseModel):
    id: str
    imdb_rating: float | None
    title: str
    file: str | None
    description: str | None
    genre: list[str] = field(default_factory=list)
    director: dict = field(default_factory=dict)
    actors_names: list[str] = field(default_factory=list)
    writers_names: list[str] = field(default_factory=list)
    actors: list[Actor] = field(default_factory=list)
    writers: list[Writer] = field(default_factory=list)


class Person(BaseModel):
    id: str
    full_name: str


class Genre(BaseModel):
    id: str
    name: str
    description: str | None
