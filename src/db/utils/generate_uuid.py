import uuid


def generate_uuid() -> str:
    """
    Generates a unique UUID (Universally Unique Identifier) string.

    This function generates a UUID version 4, which is based on random numbers.

    Returns:
        str: A unique UUID string.
    """
    return str(uuid.uuid4())
