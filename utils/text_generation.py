import uuid


def get_uuid(length: int = 10) -> str:
    return str(uuid.uuid4())[:length]