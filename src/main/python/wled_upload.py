import argparse
import sys

import requests


def main(name, args):
    parser = argparse.ArgumentParser(description='Convert YAML files to WLED JSON.')
    parser.add_argument("--host", type=str, help="Hostname to the file will be uploaded.", action="store", required=True)
    parser.add_argument("--presets", type=str, help="Presets file to be uploaded.", action="store")
    parser.add_argument("--cfg", type=str, help="Cfg file to be uploaded.", action="store")

    args = parser.parse_args()
    host = str(args.host)
    presets_file = str(args.presets)
    cfg_file = str(args.cfg)
    print("host: " + host)
    print("presets_file: " + presets_file)
    print("cfg_file: " + cfg_file)

    quit()
    test_url = 'http://192.168.196.11/upload'
    # test_url = "http://httpbin.org/post"

    test_files = {'file': ('presets.json', open('presets-off.json', 'rb'))}

    test_response = requests.post(test_url, files=test_files)

    if test_response.ok:
        print("Upload completed successfully!")
        print(test_response.text)
    else:
        print("Something went wrong!")

if __name__ == '__main__':
  main(sys.argv[0], sys.argv[1:])
