"""Handle upload and retrieval of files from S3 on Amazon AWS.
"""
import datetime
import email
import os

import boto

from bcbio import utils
from bcbio.provenance import do
from bcbio.upload import filesystem

def get_file(local_dir, bucket_name, fname, params):
    """Retrieve file from amazon S3 to a local directory for processing.
    """
    out_file = os.path.join(local_dir, os.path.basename(fname))
    if not utils.file_exists(out_file):
        metadata = []
        if params.get("reduced_redundancy"):
            metadata += ["-m", "x-amz-storage-class:REDUCED_REDUNDANCY"]
        cmd = ["gof3r", "get", "--no-md5", "-b", bucket_name, "-k", fname,
               "-p", out_file] + metadata
        do.run(cmd, "Retrieve from s3")
    return out_file

def _update_val(key, val):
    if key == "mtime":
        return val.isoformat()
    elif key in ["path", "ext"]:
        return None
    else:
        return val

def update_file(finfo, sample_info, config):
    """Update the file to an Amazon S3 bucket, using server side encryption.
    """
    conn = boto.connect_s3()
    ffinal = filesystem.update_file(finfo, sample_info, config, pass_uptodate=True)
    if os.path.isdir(ffinal):
        to_transfer = []
        for path, dirs, files in os.walk(ffinal):
            for f in files:
                full_f = os.path.join(path, f)
                k = full_f.replace(os.path.abspath(config["dir"]) + "/", "")
                to_transfer.append((full_f, k))
    else:
        k = ffinal.replace(os.path.abspath(config["dir"]) + "/", "")
        to_transfer = [(ffinal, k)]

    bucket = conn.lookup(config["bucket"])
    if not bucket:
        bucket = conn.create_bucket(config["bucket"])

    for fname, orig_keyname in to_transfer:
        keyname = os.path.join(config.get("folder", ""), orig_keyname)
        key = bucket.get_key(keyname) if bucket else None
        modified = datetime.datetime.fromtimestamp(email.utils.mktime_tz(
            email.utils.parsedate_tz(key.last_modified))) if key else None
        no_upload = key and modified >= finfo["mtime"]
        if not no_upload:
            upload_file(fname, config["bucket"], keyname, finfo)

def upload_file(fname, bucket, keyname, mditems=None):
    metadata = ["-m", "x-amz-server-side-encryption:AES256"]
    if mditems:
        for name, val in mditems.iteritems():
            val = _update_val(name, val)
            if val:
                metadata += ["-m", "x-amz-meta-%s:%s" % (name, val)]
    cmd = ["gof3r", "put", "--no-md5", "-b", bucket, "-k", keyname,
           "-p", fname] + metadata
    do.run(cmd, "Upload to s3: %s %s" % (bucket, keyname))

def upload_file_boto(fname, bucketname, keyname, mditems=None):
    """Upload a file using boto instead of external tools.
    """
    conn = boto.connect_s3()
    bucket = conn.lookup(bucketname)
    if not bucket:
        bucket = conn.create_bucket(bucketname)
    key = bucket.get_key(keyname, validate=False)
    if mditems:
        for name, val in mditems.iteritems():
            key.set_metadata(name, val)
    key.set_contents_from_filename(fname, encrypt_key=True)
