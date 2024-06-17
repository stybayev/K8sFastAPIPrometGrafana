from models import dto


class DataTransform:
    """В этом классе данные преобразуются из формата Postgres в формат, пригодный для Elasticsearch."""

    @staticmethod
    def filmwork_from_pg_to_elastic(rows: list) -> list[dto.Filmwork]:
        result: list[dto.Filmwork] = []
        for row in rows:
            actors = filter(lambda x: x["person_role"] == "actor", row["persons"])
            writers = filter(lambda x: x["person_role"] == "writer", row["persons"])
            director = filter(lambda x: x["person_role"] == "director", row["persons"])

            filmwork = dto.Filmwork(**row)
            filmwork.actors = [
                dto.Actor(id=actor["person_id"], name=actor["person_name"])
                for actor in actors
            ]
            filmwork.writers = [
                dto.Writer(id=writer["person_id"], name=writer["person_name"])
                for writer in writers
            ]
            filmwork.actors_names = [actor.name for actor in filmwork.actors]
            filmwork.writers_names = [writer.name for writer in filmwork.writers]
            filmwork.genre = row["genres"]

            director_list = [
                dto.Director(id=d["person_id"], name=d["person_name"])
                for d in director
            ]
            if director_list:
                filmwork.director = director_list[0]
            result.append(filmwork)

        return result

    @staticmethod
    def person_from_pg_to_elastic(rows: list) -> list[dto.Person]:
        return [dto.Person(id=row["id"], full_name=row["full_name"]) for row in rows]

    @staticmethod
    def genre_from_pg_to_elastic(rows: list) -> list[dto.Genre]:
        return [
            dto.Genre(id=row["id"], name=row["name"], description=row["description"])
            for row in rows
        ]
