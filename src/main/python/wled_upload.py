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

    upload(host=host, presets_file=presets_file, cfg_file=cfg_file, verbose=verbose)


def upload(*, host, presets_file=None, cfg_file=None, verbose=False):
    base_url = 'http://{host}'.format(host=host)
    work_succeeded = True
    steps_performed = 0
    if presets_file is not None:
        upload_succeeded = upload_file(base_url, presets_file, '/presets.json', verbose)
        steps_performed += 1
        work_succeeded = work_succeeded and upload_succeeded

    if work_succeeded and cfg_file is not None:
        upload_succeeded = upload_file(base_url, cfg_file, '/cfg.json', verbose)
        steps_performed += 1
        work_succeeded = work_succeeded and upload_succeeded

    if work_succeeded:
        reset_succeeded = reset_wled(base_url, verbose)
        steps_performed += 1
        work_succeeded = work_succeeded and reset_succeeded

    return steps_performed > 0 and work_succeeded


def reset_wled(base_url, verbose):
    url = '{base_url}/reset'.format(base_url=base_url)
    result = False
    if verbose:
        print("Initiating reset ... ", end='')
    try:
        reset_response = requests.get(url)
        if reset_response.ok:
            if verbose:
                print("successful.")
            result = True
        else:
            if verbose:
                print("failed.")
            print(reset_response.text)
    except Exception as ex:
        if verbose:
            print("Failed with exception.")
            print(str(ex))

    return result

def upload_file(base_url, src_file_name, dst_file_name, verbose):
    url = '{base_url}/upload'.format(base_url=base_url)
    presets_files = {'file': (dst_file_name, open(src_file_name, 'rb'), 'application/json', {'name': 'data'})}

    result = False
    if verbose:
        print("\nUploading {file} ... ".format(file=src_file_name), end='')
    try:
        upload_response = requests.post(url, files=presets_files)
        if upload_response.ok:
            if verbose:
                print("successful.")
            result = True
        else:
            if verbose:
                print("failed.")
                print(upload_response.text)
    except Exception as ex:
        if verbose:
            print("Failed with exception.")
            print(str(ex))

    return result


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
