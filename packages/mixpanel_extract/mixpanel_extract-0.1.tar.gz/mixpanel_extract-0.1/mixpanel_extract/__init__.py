import time
import urllib
import urllib2
import hashlib
import logging
log = logging.getLogger(__name__)

import boto


BASE_EXPORT_URL = 'https://data.mixpanel.com/api/2.0/export/'


def make_signed_url(base_url, api_key, api_secret, **params):
    params['api_key'] = api_key
    params.pop('sig', None)
    params['expire'] = int(time.time()) + 3600
    sorted_params = ['%s=%s' % (k, params[k]) for k in sorted(params.keys())]

    h = hashlib.md5()
    h.update(''.join(sorted_params))
    h.update(api_secret)
    params['sig'] = h.hexdigest()

    return base_url + '?' + urllib.urlencode(params)


def extract_to_fp(key, secret, from_date, to_date, retries=5, retry_sleep=60):

    url = make_signed_url(BASE_EXPORT_URL, key, secret,
                          from_date=from_date, to_date=to_date)

    log.info("Mixpanel extraction from %s", url)

    for retry in range(retries):
        if retry:
            log.warning("Waiting %ss before retrying...", retry_sleep)
            time.sleep(retry_sleep)
        try:
            response = urllib2.urlopen(url)
        except Exception as err:
            log.error("Failed to download: %s", err)
        else:
            log.info("Mixpanel download started...")
            return response.fp

    raise Exception("Failed to download after %s retry", retries)


def upload_from_fp(fp, bucket, key):
    k = boto.connect_s3().get_bucket(bucket).new_key(key)
    k.set_contents_from_file(fp, rewind=True)
