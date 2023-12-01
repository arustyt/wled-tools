

def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if file is not None and len(file) > 0 else None