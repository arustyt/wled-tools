import argparse
import sys

import requests


def main(name, args):
    parser = argparse.ArgumentParser(description='Upload WLED presets and config files to a WLED instance.')
    parser.add_argument("--host", type=str, help="Hostname to which the file(s) will be uploaded.", action="store", required=True)
    parser.add_argument("--presets", type=str, help="Presets file to be uploaded.", action="store")
    parser.add_argument("--cfg", type=str, help="Cfg file to be uploaded.", action="store")
    parser.add_argument('-v', '--verbose', action='store_true')

    args = parser.parse_args()
    host = str(args.host)
    presets_file = str(args.presets) if args.presets is not None else None
    cfg_file = str(args.cfg) if args.cfg is not None else None
    verbose = args.verbose

    if verbose:
        print("host: " + host)
        print("presets_file: " + str(presets_file))
        print("cfg_file: " + str(cfg_file))

    base_url = 'http://{host}'.format(host=host)

    file_uploaded = False

    if presets_file is not None:
        upload_succeeded = upload_file(base_url, presets_file, '/presets.json')
        if upload_succeeded:
            file_uploaded = True

    if cfg_file is not None:
        upload_succeeded = upload_file(base_url, cfg_file, '/cfg.json')
        if upload_succeeded:
            file_uploaded = True

    if file_uploaded:
        # reset_wled(base_url)
        reboot_wled(base_url)


def reboot_wled(base_url):
    url = '{base_url}/settings/sec?'.format(base_url=base_url)
    payload = 'OP=&AO=on&data=&data2='
    cookies = {'Content-Type': 'application/x-www-form-urlencoded'}
    print("Initiating reboot ... ", end='')

    try:
        reboot_response = requests.post(url, data=payload, cookies=cookies)
        if reboot_response.ok:
            print("successful.")
            result = True
        else:
            print("failed.")
            print(reboot_response.text)
    except Exception as ex:
        print("failed with exception.")
        print(str(ex))


def reset_wled(base_url):
    url = '{base_url}/reset'.format(base_url=base_url)
    print("Initiating reset ... ", end='')
    try:
        reset_response = requests.get(url)
        if reset_response.ok:
            print("successful.")
            result = True
        else:
            print("failed.")
            print(reset_response.text)
    except Exception as ex:
        print("failed with exception.")
        print(str(ex))


def upload_file(base_url, src_file_name, dst_file_name):
    url = '{base_url}/upload'.format(base_url=base_url)
    presets_files = {'file': (dst_file_name, open(src_file_name, 'rb'), 'application/json', {'name': 'data'})}

    result = False
    print("Uploading {file} ... ".format(file=src_file_name), end='')
    try:
        upload_response = requests.post(url, files=presets_files)
        if upload_response.ok:
            print("successful.")
            result = True
        else:
            print("failed.")
            print(upload_response.text)
    except Exception as ex:
        print("failed with exception.")
        print(str(ex))

    return result


if __name__ == '__main__':
  main(sys.argv[0], sys.argv[1:])
