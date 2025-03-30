# `wled_upload.py`
## Program

```
usage: wled_upload.py [-h] --host HOST [--presets PRESETS] [--cfg CFG] [-v]

Upload WLED presets and config files to a WLED instance.

options:
  -h, --help         show this help message and exit
  --host HOST        Hostname to which the file(s) will be uploaded.
  --presets PRESETS  Presets file to be uploaded.
  --cfg CFG          Cfg file to be uploaded.
  -v, --verbose
```
## Function
```
upload(*, host, presets_file=None, cfg_file=None, verbose=False)
```
