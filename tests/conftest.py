import os
import tempfile
import pytest
from src.database import Database


@pytest.fixture
def db_session():
    db_fd, db_path = tempfile.mkstemp()
    db = Database(db_name=db_path)

    yield db

    db.close()
    os.close(db_fd)
    if os.path.exists(db_path):
        os.remove(db_path)