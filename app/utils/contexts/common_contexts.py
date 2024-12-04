from contextlib import contextmanager
from app.common import constants

@contextmanager
def process_request():
    try:
        yield
    except Exception as e:
        print("Error processing request:", e)
        yield {
            "message": constants.INTERNAL_SERVER_ERROR,
            "success": False,
        }