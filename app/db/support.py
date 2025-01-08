import sqlalchemy as sa
from pygments.lexers.sql import re_prompt
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils.functions.database import _set_url_database, _sqlite_file_exists, make_url
from sqlalchemy_utils.functions.orm import quote
from typing import Optional
import logging

async def create_database_async(url: str, encoding: str = "utf8", template: Optional[str] = None) -> None:
    """
    Asynchronously create a database for the given SQLAlchemy database URL.

    :param url: Database connection URL.
    :param encoding: Encoding to use for the database (default: "utf8").
    :param template: Template to use for PostgreSQL (default: None).
    """
    url = make_url(url)
    print(url)
    database = url.database
    dialect_name = url.get_dialect().name
    dialect_driver = url.get_dialect().driver

    # Adjust the URL based on the dialect
    if dialect_name == "postgresql":
        url = _set_url_database(url, database="postgres")
    elif dialect_name == "mssql":
        url = _set_url_database(url, database="master")
    elif dialect_name == "cockroachdb":
        url = _set_url_database(url, database="defaultdb")
    elif dialect_name != "sqlite":
        url = _set_url_database(url, database=None)

    # Initialize the async engine
    if (dialect_name == "mssql" and dialect_driver in {"pymssql", "pyodbc"}) or (
        dialect_name == "postgresql" and dialect_driver in {"asyncpg", "pg8000", "psycopg2", "psycopg2cffi"}
    ):
        engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    else:
        engine = create_async_engine(url)

    try:
        if dialect_name == "postgresql":
            if not template:
                template = "template1"

            async with engine.begin() as conn:
                text = f"CREATE DATABASE {quote(conn, database)} ENCODING '{encoding}' TEMPLATE {quote(conn, template)}"
                await conn.execute(sa.text(text))

        elif dialect_name == "mysql":
            async with engine.begin() as conn:
                text = f"CREATE DATABASE {quote(conn, database)} CHARACTER SET = '{encoding}'"
                await conn.execute(sa.text(text))

        elif dialect_name == "sqlite" and database != ":memory:":
            if database and not _sqlite_file_exists(url):
                async with engine.begin() as conn:
                    await conn.execute(sa.text("CREATE TABLE DB(id int)"))
                    await conn.execute(sa.text("DROP TABLE DB"))

        else:
            async with engine.begin() as conn:
                text = f"CREATE DATABASE {quote(conn, database)}"
                await conn.execute(sa.text(text))

        logging.info(f"Database {database} created successfully.")
    except Exception as e:
        logging.error(f"Error creating database {database}: {e}")
        raise
    finally:
        await engine.dispose()
