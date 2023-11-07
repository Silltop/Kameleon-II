import hashlib
import os

import remote_data_processor


def file_checksum(filename, hash_func=hashlib.sha256, block_size=65536):
    """Calculate the checksum of a file using the specified hash function."""
    hash_object = hash_func()
    with open(filename, "rb") as file:
        for block in iter(lambda: file.read(block_size), b""):
            hash_object.update(block)
    return hash_object.hexdigest()


def compare_files(file1, file2):
    """Compare two files by calculating and comparing their checksums."""

    size1 = os.path.getsize(file1)
    size2 = os.path.getsize(file2)

    if size1 != size2:
        return False

    checksum1 = file_checksum(file1)
    checksum2 = file_checksum(file2)

    return checksum1 == checksum2


def remote_file_checksum(file_path):
    remote_data_processor.execute_command()
