from path import path


def clean_out_dir(directory):
    """
    Delete all the files and subdirectories in a directory.
    """
    if not isinstance(directory, path):
        directory = path(directory)
    for file_path in directory.files():
        file_path.remove()
    for dir_path in directory.dirs():
        dir_path.rmtree()