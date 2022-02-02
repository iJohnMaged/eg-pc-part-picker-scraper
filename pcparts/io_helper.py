import os
import errno

# Create folder if not exists
def create_folder(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
