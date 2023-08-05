import logging
import logging.handlers
import os
import sys
import traceback

from argparse import ArgumentParser
from urllib import parse
from btrfs_sxbackup.Backup import Backup
from btrfs_sxbackup.Configuration import Configuration
from btrfs_sxbackup.KeepExpression import KeepExpression
from btrfs_sxbackup.Mail import Mail
from btrfs_sxbackup import __version__

app_name = 'btrfs-sxbackup'

# Parse arguments
parser = ArgumentParser(prog=app_name)
parser.add_argument('source_subvolume', type=str,
                    help='Source subvolume to backup. Local path or SSH url.')
parser.add_argument('destination_container_subvolume', type=str,
                    help='Destination subvolume receiving snapshots. Local path or SSH url.')
parser.add_argument('-c', '--compress', action='store_true',
                    help='Enables compression during transmission, requires lzop to be installed on both source'
                         ' and destination')
parser.add_argument('-q', '--quiet', dest='quiet', action='store_true', default=False,
                    help='Do not log to STDOUT')
parser.add_argument('-sk', '--source-keep', type=str, default='10',
                    help='Expression defining which source snapshots to keep/cleanup. Can be a static number'
                         ' (of backups) or more complex expression like "1d=4/d,1w=daily,2m=none" literally'
                         ' translating to: "1 day from now keep 4 backups a day, 1 week from now keep daily backups,'
                         ' 2 months from now keep none". Default is 10')
parser.add_argument('-dk', '--destination-keep', type=str, default='10',
                    help='Expression defining which destination snapshots to keep/cleanup. Can be a static number'
                         ' (of backups) or more complex expression (see --source-keep arguemnt). Default is 10')
parser.add_argument('-ss', '--source-container-subvolume', type=str, default='sxbackup',
                    help='Override path to source snapshot container subvolume. Both absolute and relative paths\
                     are possible. Default is \'sxbackup\', relative to source subvolume')
parser.add_argument('-m', '--mail', type=str, nargs='?', const='',
                    help='Enables email notifications. If an email address is given, it overrides the'
                         ' default email-recipient setting in /etc/btrfs-sxbackup.conf')
parser.add_argument('-li', '--log-ident', dest='log_ident', type=str, default=app_name,
                    help='Log ident used for syslog logging, defaults to script name')
parser.add_argument('--version', action='version', version='%s v%s' % (app_name, __version__))
args = parser.parse_args()

# Read global configuration
config = Configuration()
config.read()

# Initialize logging
logger = logging.getLogger()
if not args.quiet:
    log_std_handler = logging.StreamHandler(sys.stdout)
    log_std_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    logger.addHandler(log_std_handler)

# Syslog handler
log_syslog_handler = logging.handlers.SysLogHandler('/dev/log')
log_syslog_handler.setFormatter(logging.Formatter(app_name + '[%(process)d] %(levelname)s %(message)s'))
logger.addHandler(log_syslog_handler)
logger.setLevel(logging.INFO)

# Log ident support
if args.log_ident:
    log_syslog_handler.ident = ' '.join([config.log_ident, args.log_ident]) + ' '

# Mail notification support
log_memory_handler = None
if args.mail is not None:
    Mail.instance().email_recipient = args.mail if len(args.mail) > 0 else config.email_recipient

    # Memory handler will buffer output for sending via mail later if needed
    log_memory_handler = logging.handlers.MemoryHandler(capacity=-1)
    log_memory_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    logger.addHandler(log_memory_handler)

logger.info('%s v%s' % (app_name, __version__))

try:
    source_url = parse.urlsplit(args.source_subvolume)
    dest_url = parse.urlsplit(args.destination_container_subvolume)
    if args.source_container_subvolume[0] == os.pathsep:
        source_container_subvolume = args.source_container_subvolume
    else:
        source_container_subvolume = os.path.join(source_url.path, args.source_container_subvolume)

    backup = Backup(
        config=config,
        source_url=source_url,
        source_container_subvolume=source_container_subvolume,
        source_keep=KeepExpression(args.source_keep),
        dest_url=dest_url,
        dest_keep=KeepExpression(args.destination_keep))

    backup.compress = args.compress

    # Perform actual backup
    backup.run()
except SystemExit as e:
    if e.code != 0:
        raise
except BaseException as e:
    # Log exception message
    e_msg = str(e)
    if len(e_msg) > 0:
        logger.error('%s' % e)

    # Log stack trace
    logger.error(traceback.format_exc())

    # Email notification
    if Mail.instance().email_recipient:
        # Format message and send
        msg = '\n'.join(map(lambda log_record: log_memory_handler.formatter.format(log_record),
                            log_memory_handler.buffer))
        Mail.instance().send('%s FAILED' % app_name, msg)
    exit(1)

exit(0)

