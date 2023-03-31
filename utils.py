"""Provide file hash calculation function."""
import hashlib

CHUNK_SIZE: int = 1024 * 1024  # one megabyte


def get_hash(path_to_file: str, chunk_size: int = CHUNK_SIZE) -> str:
    """Calculate hash of file correspond to given filepath."""
    with open(path_to_file, 'br') as in_file:
        hasher = hashlib.sha256()
        while chunk := in_file.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
