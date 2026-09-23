"""
Config de Mr Burger

    MRBURGER_DB_HOST      (localhost)
    MRBURGER_DB_PORT      (3306)
    MRBURGER_DB_USER      (Ruth)
    MRBURGER_DB_PASSWORD  ("nada pe")
    MRBURGER_DB_NAME      (mr_burguer_db)
"""

import os

DB_HOST = os.environ.get("MRBURGER_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("MRBURGER_DB_PORT", "3306"))
DB_USER = os.environ.get("MRBURGER_DB_USER", "root")
DB_PASSWORD = os.environ.get("MRBURGER_DB_PASSWORD", "123456789")
DB_NAME = os.environ.get("MRBURGER_DB_NAME", "mr_burguer_db")
