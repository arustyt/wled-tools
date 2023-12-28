from pathlib import Path

YAML_EXTENSION = '.yaml'


def build_path(directory, file):
    return "{dir}/{file}".format(dir=directory, file=file) if file is not None and len(file) > 0 else None


def find_path_list(directory: str, environment: str, files_str: str, file_base: str):
    paths = []
    if files_str is not None and len(files_str) > 0:
        for file_nickname in files_str.split(','):
            path = find_path(directory, environment, file_nickname, file_base)
            if path is not None:
                paths.append(path)

    return paths


def find_path(directory: str, environment: str, file_nickname: str, file_base: str):
    candidates = get_file_name_candidates(environment, file_nickname, file_base)

    if len(candidates) == 0:
        raise ValueError("No candidates found for '{base}' file.".format(base=file_base))

    for candidate in candidates:
        file_path = "{dir}/{file}".format(dir=directory, file=candidate) if len(candidate) > 0 else None
        if file_path is not None:
            path = Path(file_path)
            if path.is_file():
                return file_path

    raise ValueError("None of the candidate files exist: '{candidates}'.".format(candidates=str(candidates)))


def get_file_name_candidates(environment: str, file_nickname: str, file_base: str):
    candidates = []
    if file_nickname is not None and file_nickname.endswith(YAML_EXTENSION):
        candidates.append(file_nickname)
        if not file_nickname.startswith(file_base):
            candidates.append("{base}-{file}".format(base=file_base, file=file_nickname))
    else:
        if file_nickname is not None and not file_nickname.startswith(file_base):
            add_nickname_candidates(candidates, "{base}-{nickname}".format(base=file_base, nickname=file_nickname),
                                    environment)

        add_nickname_candidates(candidates, file_nickname, environment)
        add_nickname_candidates(candidates, file_base, environment)

    return candidates


def add_nickname_candidates(candidates, file_nickname, environment):
    if file_nickname is not None:
        if environment is not None:
            candidates.append("{nickname}-{env}.yaml".format(nickname=file_nickname, env=environment))

        candidates.append("{nickname}.yaml".format(nickname=file_nickname))

