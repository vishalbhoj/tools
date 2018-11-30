#!/bin/sh
set -ex

python3 ../../../test_result.py \
    -p linux-stable-rc-4.9-oe \
    -s ltp-cap_bounds-tests \
       ltp-containers-tests \
       ltp-cve-tests \
       ltp-fcntl-locktests-tests \
       ltp-filecaps-tests \
       ltp-fs_bind-tests \
       ltp-fs_perms_simple-tests \
       ltp-fsx-tests ltp-fs-tests \
       ltp-hugetlb-tests \
       ltp-io-tests \
       ltp-ipc-tests \
       ltp-math-tests \
       ltp-nptl-tests \
       ltp-open-posix-tests \
       ltp-pty-tests \
       ltp-sched-tests \
       ltp-securebits-tests \
       ltp-syscalls-tests \
       ltp-timers-tests \
    -b v4.9.142-51-gd453b6576ba5 \
    -e hi6220-hikey \
    -r True
