import logging
import os
from datetime import datetime
from uuid import uuid4

import psycopg2
import typer
from dotenv import load_dotenv
from psycopg2.extras import DictCursor
from typing_extensions import Annotated
from werkzeug.security import generate_password_hash

load_dotenv()


def create_su(
        login: Annotated[str, typer.Argument()],
        psw: Annotated[str, typer.Argument()]
):
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
            logging.error('Учетная запись администратора уже существует')
            return
        query = (
            "INSERT INTO auth.users (id, login, password, first_name, created_at) "
            f"VALUES ('{id_user}', '{login}', '{generate_password_hash(psw)}', 'admin', '{datetime.now()}')"
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
    logging.info(f'Учетная запись {login} успешно создана')
    pg_conn.close()


typer.run(create_su)
