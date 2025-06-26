import hashlib
from pathlib import Path


def file_checksum(filename, hash_func=hashlib.sha256, block_size=65536):
    """Calculate the checksum of a file using the specified hash function."""
    hash_object = hash_func()
    with open(filename, "rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            hash_object.update(block)
    return hash_object.hexdigest()


def compare_files(file1, file2):
    """Compare two files by calculating and comparing their checksums."""
    size1 = Path(file1).stat().st_size
    size2 = Path(file2).stat().st_size

    if size1 != size2:
        return False

    checksum1 = file_checksum(file1)
    checksum2 = file_checksum(file2)

    return checksum1 == checksum2
