#!/usr/bin/env python3

import os
import sys
import argparse
import re

from pprint import pprint
from multiprocessing import Pool
from subprocess import call

INFO_NAME = 'galleryinfo.txt'
INVALID_CHARS = r'[\\/:*?\"<>|]'


def main(args):
    flist = args.folders
    convert_args = []
    failure = args.failure if args.failure is not None else 'failure.txt'

    for folder in flist:
        with open(os.path.join(folder, INFO_NAME)) as fp:
            line = fp.readline()
            title = line.split(': ', maxsplit=1)[-1].strip()
            title = re.sub(INVALID_CHARS, '', title)

        if f'{title}.cbz' in args.exclude:
            if len(title) > 64:
                title = title[:64]

            print(f'{title}.cbz has been excluded, skip...')
            continue

        convert_args.append((title, folder, args.directory, failure))

    if not os.path.exists(args.directory):
        os.makedirs(args.directory, 0o755)

    with Pool() as p:
        p.map_async(work, convert_args)
        p.close()
        p.join()

    if os.path.exists(failure):
        print()
        print('failure:')

        with open(args.fail) as fp:
            for l in fp:
                l = l.strip()
                print(l.split(';')[0])

        if args.failure is None:
            os.remove(failure)


def work(args):
    title, folder, directory, failure = args

    output_path = os.path.join(directory, title)

    if os.path.exists(f'{output_path}.cbz'):
        if len(output_path) > 64:
            output_path = output_path[:64]

        print(f'{output_path}... already exists, skip...')
        return

    command = ['zip', '-jr', f'{output_path}.zip', folder]
    ret = call(command)

    if ret != 0:
        with open(failure, 'a') as fp:
            print(title, folder, sep=';', file=fp)
        return

    command = ['zip', '-d', f'{output_path}.zip', INFO_NAME]
    ret = call(command)

    if ret != 0:
        with open(failure, 'a') as fp:
            print(title, folder, sep=';', file=fp)
        return

    command = ['mv', f'{output_path}.zip', f'{output_path}.cbz']
    ret = call(command)

    if ret != 0:
        with open(failure, 'a') as fp:
            print(title, folder, sep=';', file=fp)
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folders', nargs='*', help='folders to be convert')
    parser.add_argument('-i', '--input', help='input directories list')
    parser.add_argument('-d', '--directory',
                        help='output directory', default='')
    parser.add_argument('-f', '--failure',
                        help='file that failure will be log to')
    parser.add_argument('-e', '--exclude', help='file list to be exclude')
    args = parser.parse_args()

    if args.failure is not None and os.path.exists(args.failure):
        os.remove(args.failure)

    if args.input is not None:
        with open(args.input) as fp:
            args.folders = [l.strip() for l in fp.readlines()]

    if args.exclude is not None:
        with open(args.exclude) as fp:
            args.exclude = [l.strip() for l in fp.readlines()]
    else:
        args.exclude = []

    main(args)
