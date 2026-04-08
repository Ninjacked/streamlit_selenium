import os
from dataclasses import dataclass

from dotenv import load_dotenv
import mysql.connector


load_dotenv()


@dataclass(frozen=True)
class MySQLConfig:
    host: str
    port: int
    user: str
    password: str
    database: str


def get_mysql_config() -> MySQLConfig | None:
    host = os.getenv("MYSQL_HOST", "").strip()
    user = os.getenv("MYSQL_USER", "").strip()
    password = os.getenv("MYSQL_PASSWORD", "").strip()
    database = os.getenv("MYSQL_DATABASE", "").strip()
    port_raw = os.getenv("MYSQL_PORT", "3306").strip()

    if not host or not user or not password or not database:
        return None

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise ValueError("MYSQL_PORT must be an integer") from exc

    return MySQLConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )


def get_mysql_connection():
    config = get_mysql_config()
    if config is None:
        raise ValueError(
            "Missing MySQL env vars. Set MYSQL_HOST, MYSQL_USER, "
            "MYSQL_PASSWORD, MYSQL_DATABASE, and optionally MYSQL_PORT."
        )

    return mysql.connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        database=config.database,
    )
