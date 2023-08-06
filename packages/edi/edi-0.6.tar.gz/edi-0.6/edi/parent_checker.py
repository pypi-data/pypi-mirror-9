import os

def parent_checker(filename):
    """Checks every folder above the current one for filename. Returns the full path if it exists, None if not."""
    checkdirectory = os.getcwd()
    filename_location = None

    while not os.path.ismount(checkdirectory):
        if os.path.exists(checkdirectory + os.sep + filename):
            filename_location = checkdirectory + os.sep + filename
            break
        else:
            checkdirectory = os.path.abspath(os.path.join(checkdirectory, os.pardir))

    return filename_location
