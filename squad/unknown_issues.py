#!/usr/bin/env python3

import argparse
import os


def compare(f, k):
    with open(f, 'r') as fp:
        # readlines() returns a list of lines with '\n' included.
        failures = fp.readlines()

    with open(k, 'r') as fp:
        known_issues = fp.readlines()

    filename = '{}-unknown-issues'.format(os.path.basename(f))
    with open(filename, 'w') as fp:
        for i in failures:
            if i not in known_issues:
                print(i)
                fp.write(i)
    print('unknown issues saved to: {}'.format(filename))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='failures', required=True)
    parser.add_argument('-k', dest='known_issues', required=True)
    args = parser.parse_args()
    print(args)

    compare(args.failures, args.known_issues)


if __name__ == '__main__':
    main()
