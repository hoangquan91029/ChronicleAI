import pytest
import tempfile
from pathlib import Path

from app.services.document_store import global_document_store, DB_PATH
from app.services.vector_store import global_vector_store
from app.main import ensure_sample_data_loaded


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def isolated_test_environment(tmp_path):
    """
    Guarantees test isolation across the test suite:
    1. Rebinds SQLite database to an isolated temporary file in tmp_path.
    2. Clears the in-memory vector store.
    3. Initializes standard sample fixtures deterministically.
    4. Teardown clears state and restores original DB path.
    """
    test_db = tmp_path / "test_chronicle.db"
    original_db = global_document_store.db_path

    # Rebind to isolated temp database
    global_document_store.rebind(test_db)
    global_vector_store.clear()

    # Load baseline fixtures deterministically for this test
    ensure_sample_data_loaded()

    yield

    # Clean up
    global_vector_store.clear()
    global_document_store.rebind(original_db)
