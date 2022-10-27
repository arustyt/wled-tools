import argparse
import json
import sys
# import jsondiff
import yaml
from deepdiff import DeepDiff
from pprint import pprint

import requests

def main(name, args):
    parser = argparse.ArgumentParser(description='Compare JSON/YAML files.')
    parser.add_argument('files', metavar='file', type=str, nargs=2,
                        help="files to be compared. Format: [host:]file_path")

    args = parser.parse_args()
    files = args.files
    print("files: " + str(files))

    source_file = files[0]
    target_file = files[1]

    source_data = load_file_data(source_file)
    target_data = load_file_data(target_file)

    result = DeepDiff(source_data, target_data, verbose_level=2)

#    diffs = json.dumps(result, indent=2)

    pprint(result, indent=2)


def get_download_url_from_file_spec(file_spec: str):
    parts = file_spec.split(':')
    host = parts[0]
    file = parts[1]

    url = "http://{host}/{file}?download".format(host=host, file=file)

    return url


def load_remote_file_data(file: str):
    url = get_download_url_from_file_spec(file)
    result = requests.get(url)
    file_data = json.loads(result.content)
    return file_data


def is_remote_file(file: str):
    return ':' in file


def load_yaml_file_data(file: str):
    file_data = yaml.safe_load(open(file))
    return file_data


def is_yaml_file(file: str):
    return ':' not in file and file.endswith('.yaml')


def load_json_file_data(file: str):
    file_data = json.load(open(file))
    return file_data


def is_json_file(file: str):
    return ':' not in file and file.endswith('.json')


def load_file_data(file: str):
    file_data = {}

    if is_remote_file(file):
        file_data = load_remote_file_data(file)
    elif is_yaml_file(file):
        file_data = load_yaml_file_data(file)
    elif is_json_file(file):
        file_data = load_json_file_data(file)
    else:
        raise FileNotFoundError("File type could not be identified: " + file)

    return file_data


if __name__ == '__main__':
  main(sys.argv[0], sys.argv[1:])
