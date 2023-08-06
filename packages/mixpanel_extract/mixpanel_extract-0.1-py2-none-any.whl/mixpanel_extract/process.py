import os
import gzip
import shutil
from tempfile import NamedTemporaryFile
import logging
log = logging.getLogger(__name__)

from mixpanel_extract import extract_to_fp, upload_from_fp


def process(args):
    if args.output:
        with open(args.output, 'wb+') as fp:
            store(args, fp)
    else:
        with NamedTemporaryFile(prefix='mixpanel-') as fp:
            store(args, fp)


def store(args, output_fp):
    log.info("Downloading from Mixpanel...")
    download_fp = extract_to_fp(key=args.mixpanel_key,
                                secret=args.mixpanel_secret,
                                from_date=args.from_date,
                                to_date=args.to_date)

    log.info("Storing to %s...", output_fp.name)

    if args.gzip:
        log.info("Also compressing...")
        fp = gzip.GzipFile(fileobj=output_fp)
        shutil.copyfileobj(download_fp, fp)
    else:
        shutil.copyfileobj(download_fp, output_fp)

    if args.s3_bucket:
        if args.s3_prefix:
            key = os.path.join(args.s3_prefix, args.s3_key)
        else:
            key = args.s3_key
        log.info("Uploading to s3://%s/%s...", args.s3_bucket, key)
        upload_from_fp(fp=output_fp, bucket=args.s3_bucket, key=key)
