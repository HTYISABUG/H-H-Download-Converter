#!/usr/bin/env python3

import os
import sys
import argparse
import re

from multiprocessing import Pool
from subprocess import call

INFO_NAME = 'galleryinfo.txt'
INVALID_CHARS = r'[\\/:*?\"<>|]'


def main(args):
    flist = args.folders
    convert_args = []

    for folder in flist:
        with open(os.path.join(folder, INFO_NAME)) as fp:
            line = fp.readline()
            title = line.split(': ', maxsplit=1)[-1].strip()
            title = re.sub(INVALID_CHARS, '', title)

        convert_args.append((title, folder, args.dir, args.fail))

    with Pool() as p:
        p.map_async(work, convert_args)
        p.close()
        p.join()

    if os.path.exists(args.fail):
        print()
        print('failure:')

        with open(args.fail) as fp:
            for l in fp:
                l = l.strip()
                print(l.split(';')[0])


def work(args):
    if not os.path.exists(args[2]):
        os.makedirs(args[2], 0o755)

    output_path = os.path.join(args[2], args[0])

    if os.path.exists(f'{output_path}.cbz'):
        if len(output_path) > 32:
            output_path = output_path[:64]

        print(f'{output_path}... already exists, skip...')
        return

    command = ['zip', '-jr', f'{output_path}.zip', args[1]]
    ret = call(command)

    if ret != 0:
        with open(args[3], 'a') as fp:
            print(args[0], args[1], sep=';', file=fp)
        return

    command = ['zip', '-d', f'{output_path}.zip', INFO_NAME]
    ret = call(command)

    if ret != 0:
        with open(args[3], 'a') as fp:
            print(args[0], args[1], sep=';', file=fp)
        return

    command = ['mv', f'{output_path}.zip', f'{output_path}.cbz']
    ret = call(command)

    if ret != 0:
        with open(args[3], 'a') as fp:
            print(args[0], args[1], sep=';', file=fp)
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('folders', nargs='*', help='folders to be convert')
    parser.add_argument('-i', '--input', help='input directories list')
    parser.add_argument('-d', '--dir', help='output directory', default='')
    parser.add_argument('--fail', help='output failure', default='fail.txt')
    args = parser.parse_args()

    if os.path.exists(args.fail):
        os.remove(args.fail)

    if args.input is not None:
        with open(args.input) as fp:
            args.folders = [l.strip() for l in fp.readlines()]

    main(args)
