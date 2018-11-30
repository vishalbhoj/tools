#!/bin/sh
set -ex

python3 ../../../test_result.py \
    -p aosp-master-tracking \
    -s "vts-test/arm64-v8a.VtsKernelLtp" \
    -e "hi6220-hikey_4.4" \
    -r False
