import typer
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv
from uuid import uuid4
from psycopg2.extras import DictCursor
from passlib.hash import pbkdf2_sha256

load_dotenv()


def create_su(login: str, psw: str):
    dsl = {
        'dbname': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'host': os.getenv('UVICORN_HOST'),
        'port': os.getenv('POSTGRES_PORT')
    }

    with psycopg2.connect(**dsl, cursor_factory=DictCursor) as pg_conn:
        cursor = pg_conn.cursor()
        id_user = uuid4()
        id_role = uuid4()
        try:
            query = (
                "INSERT INTO auth.roles (id, name, permissions) "
                "VALUES ('" + str(id_role) + "', 'admin', '{admin}')"
            )
            cursor.execute(query)
            pg_conn.commit()
        except psycopg2.errors.UniqueViolation:
            print('Учетная запись администратора уже существует.')
            return
        query = (
            "INSERT INTO auth.users (id, login, password, first_name, created_at) "
            f"VALUES ('{id_user}', '{login}', '{pbkdf2_sha256.hash(psw)}', 'admin', '{datetime.now()}')"
        )
        cursor.execute(query)
        pg_conn.commit()
        query = (
            "INSERT INTO auth.user_roles (id, user_id, role_id) "
            f"VALUES ('{uuid4()}', '{id_user}', '{id_role}')"
        )
        cursor.execute(query)
        pg_conn.commit()
        cursor.close()
    print(f'Учетная запись {login} успешно создана')
    pg_conn.close()


typer.run(create_su)

