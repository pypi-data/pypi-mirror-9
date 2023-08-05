from __future__ import print_function
import plac
import boto
import sys
import calendar
import datetime


def error(*objs):
    print("ERROR", *objs, end='\n', file=sys.stderr)


@plac.annotations(
    profile_name=("""Name of boto profile to use for credentials""", "option"),
    aws_access_key_id=("Your AWS Access Key ID", "option"),
    aws_secret_access_key=("Your AWS Secret Access Key", "option"),
    validate_bucket=("Make sure, the bucket really exists", "flag"),
    validate_key=("Make sure, the key really exists", "flag"),
    http=("Force the url to use http and not https", "flag"),
    expire_dt=("ISO formatted time of expiration, full seconds,"
               " 'Z' is obligatory, e.g. '2014-02-14T21:47:16Z'"),
    bucket_name="name of bucket", key_names="key names to generate tmpurl for")
def main(
        expire_dt,
        bucket_name,
        profile_name=None,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        validate_bucket=False,
        validate_key=False,
        http=False,
        *key_names):
    """Generate temporary url for accessing content of AWS S3 key.

    Temporary url includes expiration time, after which it rejects serving the
    content.

    Urls are printed one per line to stdout.

    For missing key names empty line is printed and error goes to stderr.

    If the bucket is versioned, tmp url will serve the latest version
    at the moment of request (version_id is not part of generated url).

    By default, bucket and key name existnence is not verified.

    Url is using https, unless `-http` is used.
    """
    expire_dt = datetime.datetime.strptime(expire_dt, "%Y-%m-%dT%H:%M:%SZ")
    expire = calendar.timegm(expire_dt.timetuple())
    try:
        con = boto.connect_s3(profile_name=profile_name)
    except Exception as e:
        error("Unable to connect to AWS S3, check your credentials", e)
        return
    try:
        validate = validate_bucket or validate_key
        bucket = con.get_bucket(bucket_name, validate=validate)
    except boto.exception.S3ResponseError as e:
        error("Error: Bucket not found: ", bucket_name)
        return
    for key_name in key_names:
        if validate_key:
            key = bucket.get_key(key_name)
            if key is None:
                error("Error: missing key: ", key_name)
                print("")
                continue
        # get a key object without version_id
        # (otherwise we get url to specific version)
        key = boto.s3.key.Key(bucket, key_name)
        print(key.generate_url(expires_in=expire,
                               expires_in_absolute=True,
                               force_http=http)
              )


def placer():
    try:
        plac.call(main)
    except Exception as e:
        error(e)

if __name__ == "__main__":
    placer()
