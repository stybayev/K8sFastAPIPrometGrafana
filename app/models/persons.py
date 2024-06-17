from app.models.base_model import BaseMixin, PaginatedParams


class Person(BaseMixin):
    full_name: str


class FilmPerson(BaseMixin):
    name: str


class Persons(Person, PaginatedParams):
    pass


class Actor(FilmPerson):
    pass


class Writer(FilmPerson):
    pass


class Director(FilmPerson):
    pass
