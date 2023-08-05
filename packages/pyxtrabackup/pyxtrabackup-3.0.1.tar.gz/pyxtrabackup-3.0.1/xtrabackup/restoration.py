"""Xtrabackup script

Usage:
    pyxtrabackup-restore --base-archive=<base_archive_path> --incremental-archive=<incremental_archive_path> --user=<user> [--password=<pwd>] [--data-dir=<data_dir>] [--restart] [--tmp-dir=<tmp>] [--log-file=<log>] [--out-file=<log>] [--backup-threads=<threads>]
    pyxtrabackup-restore (-h | --help)
    pyxtrabackup --version


Options:
    -h --help                                   Show this screen.
    --version                                   Show version.
    --user=<user>                               MySQL user.
    --password=<pwd>                            MySQL password.
    --base-archive=<archive_path>               Base backup.
    --incremental-archive=<archive_path>        Incremental archive target.
    --data-dir=<data_dir>                       MySQL server data directory [default: /var/lib/mysql]
    --restart                                   Restart the server after backup restoration.
    --tmp-dir=<tmp>                             Temporary directory [default: /tmp].
    --log-file=<log>                            Log file [default: /var/log/mysql/pyxtrabackup-restore.log].
    --out-file=<log>                            Output file [default: /var/log/mysql/xtrabackup.out].
    --backup-threads=<threads>                  Threads count [default: 1].

"""
from docopt import docopt
import sys
import logging
from xtrabackup.restoration_tools import RestorationTool


def main():
    arguments = docopt(__doc__, version='3.0.0')
    restore_tool = RestorationTool(arguments['--log-file'],
                                   arguments['--out-file'],
                                   arguments['--data-dir'])
    try:
        restore_tool.start_restoration(arguments['--base-archive'],
                                       arguments['--incremental-archive'],
                                       arguments['--tmp-dir'],
                                       arguments['--restart'])
    except Exception:
        logger = logging.getLogger(__name__)
        logger.error("pyxtrabackup failed.")
        exit(1)
    exit(0)


if __name__ == '__main__':
    sys.exit(main())
