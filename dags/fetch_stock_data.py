import os
import time
import logging
import requests
import psycopg2
from psycopg2 import pool
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Config
API_URL = os.getenv("API_URL")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", "5432")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 5))
BATCH_SIZE = int(os.getenv("BATCH_SIZE", 500))

# Logging setup
logging.basicConfig(
    format="%(asctime)s [%(levelname)s]: %(message)s",
    level=logging.INFO
)

# Database connection pool
db_pool = None


def init_db_pool():
    """Initialize PostgreSQL connection pool."""
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(
            1, 5,  # minconn, maxconn
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )


def fetch_stock_data() -> List[Dict[str, Any]]:
    """
    Fetch stock market data from API with retries and validation.
    Returns only valid records.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            if not isinstance(data, list):
                raise ValueError("API returned unexpected format: expected a list")

            valid_data = []
            for item in data:
                if {"symbol", "price", "date"}.issubset(item):
                    valid_data.append(item)
                else:
                    logging.warning(f"Skipping invalid record: {item}")

            return valid_data

        except requests.Timeout:
            logging.error(f"[Attempt {attempt+1}] API request timed out.")
        except requests.RequestException as e:
            logging.error(f"[Attempt {attempt+1}] Network/API error: {e}")
        except ValueError as e:
            logging.error(f"[Attempt {attempt+1}] Data validation error: {e}")

        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_DELAY)

    logging.critical("Failed to fetch data after retries.")
    return []


def store_stock_data(stock_data: List[Dict[str, Any]]):
    """
    Store stock data in PostgreSQL in batches with UPSERT to avoid duplicates.
    """
    if not stock_data:
        logging.warning("No stock data to insert.")
        return

    init_db_pool()
    conn = None
    try:
        conn = db_pool.getconn()
        cur = conn.cursor()

        insert_query = """
        INSERT INTO stock_data (symbol, price, date)
        VALUES %s
        ON CONFLICT (symbol, date) DO UPDATE SET
            price = EXCLUDED.price;
        """

        # Batch insert for scalability
        for i in range(0, len(stock_data), BATCH_SIZE):
            batch = stock_data[i:i+BATCH_SIZE]
            values = [(item["symbol"], item["price"], item["date"]) for item in batch]
            execute_values(cur, insert_query, values)
            logging.info(f"Inserted/updated {len(batch)} records.")

        conn.commit()
        cur.close()

    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            db_pool.putconn(conn)


def fetch_and_store():
    """
    Wrapper function for Airflow to fetch and store stock data in one call.
    """
    data = fetch_stock_data()
    store_stock_data(data)


if __name__ == "__main__":
    fetch_and_store()
