import os

import pymysql
from dotenv import load_dotenv
from pymysql.constants import CLIENT

load_dotenv()


def get_connection():
    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        # Matched rows count as success even when the submitted value is unchanged.
        client_flag=CLIENT.FOUND_ROWS,
    )
