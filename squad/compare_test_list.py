#!/usr/bin/env python3

import argparse
import os


def compare(f1, f2, type):
    with open(f1, 'r') as fp:
        # readlines() returns a list of lines with '\n' included.
        list1 = fp.readlines()

    with open(f2, 'r') as fp:
        list2 = fp.readlines()

    filename = '{}-{}-{}'.format(os.path.basename(f1), os.path.basename(f2), type)
    if type == 'common':
        data = set(list1) & set(list2)
    elif type == 'differ':
        data = set(list1) - set(list2)
    with open(filename, 'w') as fp:
        for i in data:
            fp.write(i)
    print('{} elements saved to: {}'.format(type, filename))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f1', dest='file1', required=True)
    parser.add_argument('-f2', dest='file2', required=True)
    parser.add_argument('-t', dest='type', default='common', choices=['common', 'differ'])
    args = parser.parse_args()
    print(args)

    compare(args.file1, args.file2, args.type)


if __name__ == '__main__':
    main()
