"""
Simple factory wrapper for the Postgres database handler.  With SQLite no
longer supported the module simply re‑exports ``database.DatabaseHandler``.
Other code can import ``get_handler`` as a convenience.
"""

# This project now uses PostgreSQL exclusively.  The previous
# sqlite fallback has been removed.

from database import DatabaseHandler  # type: ignore

# make handler available under a function as well

def get_handler(*args, **kwargs):
    """Return a new database handler instance, passing through any arguments."""
    return DatabaseHandler(*args, **kwargs)
