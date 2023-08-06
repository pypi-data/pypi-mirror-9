import os
import sys
import argparse
import datetime
import logging
log = logging.getLogger(__name__)

from mixpanel_extract.process import process


def setup_logging(level=logging.INFO, console=True):
    root = logging.getLogger()
    root.setLevel(level)

    if console:
        sh = logging.StreamHandler()
        sh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)-8s %(name)-25s %(message)s')
        sh.setFormatter(formatter)
        root.addHandler(sh)

    sl = logging.handlers.SysLogHandler(
        address='/dev/log',
        facility=logging.handlers.SysLogHandler.LOG_LOCAL3)
    sl.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        'module=%(name)s function=%(funcName)s line=%(lineno)d %(message)s')
    sl.setFormatter(formatter)
    root.addHandler(sl)

    # Boto debug level is just too crazy
    log_boto = logging.getLogger('boto')
    log_boto.setLevel(logging.INFO)


# Using the proleptic Gregorian calendar is a solid solution for the
# next/previous day problem
# http://en.wikipedia.org/wiki/Proleptic_Gregorian_calendar

def make_yesterday_isoformat():
    yesterday_as_day = datetime.date.today().toordinal() - 1
    return datetime.date.fromordinal(yesterday_as_day).isoformat()


def parse_args(progname, description):
    parser = argparse.ArgumentParser(prog=progname, description=description)

    default_yesterday = make_yesterday_isoformat()

    default_mixpanel_api_key = os.environ.get('MIXPANEL_KEY')
    default_mixpanel_api_secret = os.environ.get('MIXPANEL_SECRET')

    default_s3_bucket = os.environ.get('S3_BUCKET')
    default_s3_prefix = os.environ.get('S3_PREFIX', default_mixpanel_api_key)
    default_s3_key = os.environ.get('S3_KEY', default_yesterday)
    default_output = os.environ.get('OUTPUT')

    parser = argparse.ArgumentParser()

    parser.add_argument('--mixpanel-key',
                        default=default_mixpanel_api_key,
                        help='Mixpanel API key [default=%(default)s]')
    parser.add_argument('--mixpanel-secret',
                        default=default_mixpanel_api_secret,
                        help='Mixpanel API secret [default=%(default)s]')

    parser.add_argument('--s3-bucket',
                        default=default_s3_bucket,
                        help='Store on S3 [default=%(default)s]')
    parser.add_argument('--s3-prefix',
                        default=default_s3_prefix,
                        help='Prefix for the S3 key [default=%(default)s]')
    parser.add_argument('--s3-key',
                        default=default_s3_key,
                        help='Prefix for the S3 key [default=%(default)s]')

    parser.add_argument('-o', '--output',
                        default=default_output,
                        help='Store in local filesystem [default=%(default)s]')

    parser.add_argument('-z', '--gzip',
                        action='store_true',
                        help='Store as GZIP file')

    parser.add_argument('--from-date',
                        metavar='YYYY-MM-DD',
                        default=default_yesterday,
                        help='Extract events from this date '
                             '[default=%(default)s]')
    parser.add_argument('--to-date',
                        metavar='YYYY-MM-DD',
                        default=default_yesterday,
                        help='Extract events up to this date '
                             '[default=%(default)s]')

    args = parser.parse_args()

    if not args.mixpanel_key:
        parser.exit("Missing arguments: mixpanel-key")
    if not args.mixpanel_secret:
        parser.exit("Missing arguments: mixpanel-secret")

    if not (args.s3_bucket or args.output):
        parser.exit("Missing arguments: --s3-bucket or --output")

    return args


def mixpanel_extract():
    setup_logging()
    args = parse_args('mixpanel-extract',
                      'Extract Mixpanel raw events and store on S3')
    try:
        log.warning("Starting processing")
        process(args)
        log.warning("End of processing")
    except (KeyboardInterrupt, SystemExit):
        log.warning("Processing interrupted")
        sys.exit(1)
    except:
        log.exception("Processing failed")
