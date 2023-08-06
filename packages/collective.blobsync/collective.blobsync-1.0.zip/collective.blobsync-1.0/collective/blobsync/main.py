""

from copyblobs import backup_blobs

import argparse


def main():
    parser = argparse.ArgumentParser(description='Rotating generational rsync backup.')
    parser.add_argument('src', help='rsync source')
    parser.add_argument('dest', help='rsync destination')
    parser.add_argument('--keep', default=7, type=int, help='Number of generations to keep')
    parser.add_argument('--rsync-options', dest="options", default="", help='rsync option arguments')
    args = parser.parse_args()

    backup_blobs(args.src, args.dest, keep_blob_days=args.keep, rsync_options=args.options)
