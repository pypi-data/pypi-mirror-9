Introduction
============

This package is a wrapper around the backup_blobs component of collective.recipe.backup. There are no dependencies beyond Python 2.6-7 and having rsync installed.

collective.recipe.backup has a wonderful mechanism for a rotating generational backkup via rsync. The really clever thing is that it can use rsync's hard link feature to minimize storage space.

collective.recipe.backup was developed by Reinout van Rees and Maurits van Rees, both from Zest software. The blob backups feature was added by Matej Cotman (niteoweb). collective.recipe backup is GPL; so is this package.

This package borrows two Python source files from collective.recipe.backup. The only change made is to one import to remove a dependency.

This package exposes c.r.b's backup_blobs function as collective.blobsync.backup_blobs. The prototype for that function is::

    def backup_blobs(source, destination, full=False, use_rsync=True,
                     keep=0, keep_blob_days=0, gzip_blob=False, rsync_options='')

The package also creates a command-line script for the most common (IMHO) usage::

    usage: blobsync [-h] [--keep KEEP] [--rsync-options OPTIONS] src dest

    Rotating generational rsync backup.

    positional arguments:
      src                   rsync source
      dest                  rsync destination

    optional arguments:
      -h, --help            show this help message and exit
      --keep KEEP           Number of generations to keep
      --rsync-options OPTIONS
                            rsync option arguments

Note that src and dest may be rsync-format source and destination. Thus, they may be remote, not just local.

Example Usage
=============

This is example usage with an rsync daemon. The rsync "live" share is a Plone var directory::

    blobsync \
    	backup_user@www.YOURSERVERHERE.org::live/blobstorage \
    	/mnt/backup/www_live/blobstoragebackups \
    	--keep=14 \
    	--rsync-options='--password-file=rsync_secret'
