"""
Database helper for community seeding scripts.
Provides PostgreSQL connection from DATABASE_URL and cuid generation.
"""

from __future__ import annotations

import os
import random
import string
import time
from urllib.parse import urlparse

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    """Get a PostgreSQL connection from DATABASE_URL."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL not set in .env")

    parsed = urlparse(url)
    return psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        dbname=parsed.path.lstrip("/"),
        user=parsed.username,
        password=parsed.password,
    )


def generate_cuid() -> str:
    """Generate a cuid-like ID compatible with Prisma."""
    timestamp = int(time.time() * 1000)
    random_part = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    return f"c{timestamp:x}{random_part}"
