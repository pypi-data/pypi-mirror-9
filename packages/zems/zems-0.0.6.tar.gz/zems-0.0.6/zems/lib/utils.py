import os


def find_files_by_extension(path, extension):
    if not extension.startswith("."):
        extension = "." + extension

    files = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk(path)
        for filename in files if filename.endswith(extension)
    ]

    if len(files) < 1:
        raise IOError("No files found with extension %s" % extension)

    return files


def find_files(path, name):
    files = [
        os.path.join(root, filename)
        for root, dirs, files in os.walk(path)
        for filename in files if name in filename
    ]

    if len(files) < 1:
        raise IOError("No files found with name %s" % name)

    return files


def determine_newest_file(files):
    modified_at = 0
    newest_file = None

    for filename in files:
        tmp = os.path.getmtime(filename)
        if tmp > modified_at:
            modified_at = tmp
            newest_file = filename

    return newest_file