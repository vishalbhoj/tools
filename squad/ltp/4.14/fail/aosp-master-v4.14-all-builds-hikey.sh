#!/bin/sh
set -ex

# ltp test failures from lkft-aosp 4.14 on hikey
python3 ../../../test_result.py \
    -p aosp-master-tracking \
    -s "vts-test/arm64-v8a.VtsKernelLtp" \
    -e "hi6220-hikey_4.14" \
    -r False
