import argparse
import sys

import requests


def main(name, args):
    parser = argparse.ArgumentParser(description='Upload WLED presets and config files to a WLED instance.')
    parser.add_argument("--host", type=str, help="Hostname to which the file(s) will be uploaded.", action="store", required=True)
    parser.add_argument("--presets", type=str, help="Presets file to be uploaded.", action="store")
    parser.add_argument("--cfg", type=str, help="Cfg file to be uploaded.", action="store")

    args = parser.parse_args()
    host = str(args.host)
    presets_file = str(args.presets) if args.presets is not None else None
    cfg_file = str(args.cfg) if args.cfg is not None else None
    print("host: " + host)
    print("presets_file: " + str(presets_file))
    print("cfg_file: " + str(cfg_file))

    url = 'http://{host}/upload'.format(host=host)
    # print("URL: " + url)

    if presets_file is not None:
        upload_file(url, presets_file, 'presets.json')

    if cfg_file is not None:
        upload_file(url, cfg_file, 'cfg.json')


def upload_file(url, src_file_name, dst_file_name):
    presets_files = {'file': (dst_file_name, open(src_file_name, 'rb'))}
    # print("presets_files: " + str(presets_files))
    try:
        upload_response = requests.post(url, files=presets_files)
        if upload_response.ok:
            print("{file} upload completed successfully!".format(file=src_file_name))
        else:
            print("{file} upload failed.".format(file=src_file_name))
            print(upload_response.text)
    except Exception as ex:
        print("{file} upload failed.".format(file=src_file_name))
        print(str(ex))


if __name__ == '__main__':
  main(sys.argv[0], sys.argv[1:])
