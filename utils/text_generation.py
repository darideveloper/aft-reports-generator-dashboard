import uuid


def get_uuid(length: int = 8) -> str:
    return str(uuid.uuid4())[:length]