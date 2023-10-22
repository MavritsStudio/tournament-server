from uuid import uuid4


def get_uuid_hex() -> str:
    return uuid4().hex
