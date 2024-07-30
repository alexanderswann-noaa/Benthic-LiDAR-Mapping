import os
import sys
import py7zr


def extract_7z(archive_path, extract_path):
    """
    Used to extract the contents of a .7z file in the provided directory

    :param archive_path:
    :param extract_path:
    :return:
    """
    # Ensure the extraction directory exists
    os.makedirs(extract_path, exist_ok=True)

    # Open and extract the 7z archive
    with py7zr.SevenZipFile(archive_path, mode='r') as archive:
        archive.extractall(path=extract_path)

    print(f"Extracted contents to: {extract_path}")


if __name__ == "__main__":

    # The assumed location of the .7z file within the build folder
    dst_dir = './build'
    src_path = './build/CloudComPy310_20240613.7z'
    assert os.path.exists(src_path), "ERROR: Cannot find .7z file in ./build"

    # The destination to extract the .7z file within the build folder
    extract_7z(src_path, dst_dir)
    print("Done.")