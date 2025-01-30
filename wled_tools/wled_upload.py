import argparse
import sys

import requests

from wled_utils.logger_utils import get_logger, init_logger


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

    init_logger()

    if verbose:
        get_logger().info("host: " + host)
        get_logger().info("presets_file: " + str(presets_file))
        get_logger().info("cfg_file: " + str(cfg_file))

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
        get_logger().info("Initiating reset ... ")
    try:
        reset_response = requests.get(url)
        if reset_response.ok:
            if verbose:
                get_logger().info("successful.")
            result = True
        else:
            get_logger().error("Reset failed.")
            get_logger().error(reset_response.text)
    except Exception as ex:
        get_logger().error("Reset failed with exception.")
        get_logger().error(str(ex))

    return result


def upload_file(base_url, src_file_name, dst_file_name, verbose):
    url = '{base_url}/upload'.format(base_url=base_url)
    presets_files = {'file': (dst_file_name, open(src_file_name, 'rb'), 'application/json', {'name': 'data'})}

    result = False
    if verbose:
        get_logger().info("Uploading {file} ... ".format(file=src_file_name))
    try:
        upload_response = requests.post(url, files=presets_files)
        if upload_response.ok:
            if verbose:
                get_logger().info("successful.")
            result = True
        else:
            get_logger().error("upload_file, {}, failed.".format(src_file_name))
            get_logger().error(upload_response.text)
    except Exception as ex:
        get_logger().error("upload_file, {}, failed with exception.".format(src_file_name))
        get_logger().error(str(ex))

    return result


if __name__ == '__main__':
    main(sys.argv[0], sys.argv[1:])
