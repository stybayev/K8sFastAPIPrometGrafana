import uuid


def generate_person(count: int):
    return [{'id': str(uuid.uuid4()), 'name': 'Ann'} for _ in range(count)]


def generate_films_without_test_person(count: int):
    return [
        {
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genre': ['Action', 'Sci-Fi'],
            'title': 'The Star',
            'description': 'New World',
            'director': {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'},
            'actors_names': ['Ann', 'Bob'],
            'writers_names': ['Ben', 'Howard'],
            'actors': [
                {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'name': 'Bob'}
            ],
            'writers': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ]
        } for _ in range(count)]
