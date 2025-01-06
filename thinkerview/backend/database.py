import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()


def open_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )


def close_connection(conn):
    conn.close()


def create_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id SERIAL PRIMARY KEY,
                title TEXT,
                date DATE,
                description TEXT,
                categories TEXT[],
                url TEXT UNIQUE,
                thumbnail_url TEXT,
                youtube_url TEXT,
                interviewees JSONB[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


if __name__ == "__main__":
    conn = open_connection()
    create_table(conn)
    close_connection(conn)
