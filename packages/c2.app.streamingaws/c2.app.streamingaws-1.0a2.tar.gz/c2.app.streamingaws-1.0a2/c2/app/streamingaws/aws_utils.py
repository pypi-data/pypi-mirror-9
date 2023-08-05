# coding: utf-8
import time
from datetime import datetime
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from boto.iam.connection import IAMConnection
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.lifecycle import Lifecycle
from boto.cloudfront import CloudFrontConnection
from boto.cloudfront.distribution import Distribution
from boto.cloudfront.origin import S3Origin
from boto.cloudfront.signers import TrustedSigners
from boto.cloudfront.logging import LoggingInfo
# from boto.cloudfront.distribution import DistributionConfig
# from boto.cloudfront.identity import OriginAccessIdentity
from boto.elastictranscoder.layer1 import ElasticTranscoderConnection
from boto.regioninfo import RegionInfo
from boto.exception import BotoServerError, S3ResponseError

from c2.app.streamingaws.controlpanel.interfaces import IStreamingAwsControlPanel



def _get_settings():
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IStreamingAwsControlPanel)
    return settings

def get_access_key():
    settings = _get_settings()
    access_key_id = settings.access_key_id
    secret_access_key = settings.secret_access_key
    if access_key_id and secret_access_key:
        return access_key_id, secret_access_key
    return None, None

def get_region():
    settings = _get_settings()
    region_name = settings.region_name
    if region_name:
        return RegionInfo(endpoint=region_name)
    return None

def get_iam_conn():
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    conn = IAMConnection(access_key_id, secret_access_key)
    return conn

def get_s3_bucket(bucket_name):
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    conn = S3Connection(access_key_id, secret_access_key)
    try:
        bucket_obj = conn.get_bucket(bucket_name)
    except S3ResponseError:
        return None
    return bucket_obj

def get_trans_coder_conn():
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    region = get_region()
    if not region:
        return None
    conn = ElasticTranscoderConnection(
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    region=region)
    return conn

def get_cloudfront_dist():
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    conn = CloudFrontConnection(access_key_id, secret_access_key)
    distribution = Distribution(connection=conn, config=None,
                                domain_name='', id='',
                                last_modified_time=None, status='')
    return distribution

def get_cloudfront_keys():
    settings = _get_settings()
    cloudfront_key_id = settings.cloudfront_key_id
    cloudfront_private_key_str = settings.cloudfront_private_key_str
    if cloudfront_key_id and cloudfront_private_key_str:
        return cloudfront_key_id, cloudfront_private_key_str
    return None, None

def get_signed_url(url, policy_url=None, expire=7200):
    cloudfront_key_id, cloudfront_private_key_str = get_cloudfront_keys()
    if cloudfront_key_id is None or cloudfront_private_key_str is None:
        return None
    distribution = get_cloudfront_dist()
    if distribution is None:
        return None
    expire_time = int(time.time() + expire)
    signed_url = distribution.create_signed_url(url=url,
                            keypair_id=cloudfront_key_id,
                            expire_time=expire_time,
                            policy_url=policy_url,
                            private_key_string=cloudfront_private_key_str)
    return signed_url


def _get_pipeline_name_to_id(pipelines, name):
    for pipeline in pipelines:
        if pipeline.get(u'Name') == name:
            if pipeline.get(u'Status') == u'Active':
                return pipeline.get(u'Id')
    return None


def create_new_transcoder_pipeline(et_conn, pipeline_name):
    settings = _get_settings()
    input_bucket = settings.temp_bucket_name
    output_bucket = settings.private_bucket_name
    if not input_bucket or not output_bucket:
        return None
    iam_conn = get_iam_conn()
    if iam_conn is None:
        return None
    try:
        et_roles = iam_conn.get_role("Elastic_Transcoder_Default_Role")
        role = et_roles[u"get_role_response"][u"get_role_result"][u"role"][u"arn"]
    except BotoServerError:
        et_roles = iam_conn.create_role("Elastic_Transcoder_Default_Role")
        role = et_roles[u"create_role_response"][u"create_role_result"][u"role"][u"arn"]
    notifications = {"Progressing":"", "Completed":"", "Warning":"", "Error":""}

    pipeline = et_conn.create_pipeline(name=pipeline_name,
                         input_bucket=input_bucket,
                         output_bucket=output_bucket,
                         role=role,
                         notifications=notifications)
    return pipeline.get(u'Pipeline', {}).get(u"Id")

def send_file_to_bucket(bucket, key, file_data):
    bucket_obj = get_s3_bucket(bucket)
    k = Key(bucket_obj)
    k.key = key
    k.set_contents_from_string(file_data)
    return True

# def copy_file_between_bucket(src_bucket, src_key, dist_bucket, dist_key):
#     dist_bucket_obj = get_s3_bucket(dist_bucket)
#     if dist_bucket_obj is None:
#         return None
#     old_key = dist_bucket_obj.get_key(dist_key)
#     if old_key is not None:
#         old_key.delete()
#     dist_bucket_obj.copy_key(dist_key, src_bucket, src_key)
#     return True

# def send_file_to_bucket_and_copy(path, filename, file_data):
#     settings = _get_settings()
#     src_bucket = settings.temp_bucket_name
#     dist_bucket = settings.private_bucket_name
#     private_prefix = settings.private_bucket_sub_folder
#     src_key = "/".join([path, filename])
#     if private_prefix:
#         dist_key = "/".join([private_prefix, src_key])
#     else:
#         dist_key = src_key
#     send_file_to_bucket(src_bucket, src_key, file_data)
#     copy_file_between_bucket(src_bucket, src_key, dist_bucket, dist_key)

def send_file_to_bucket_from_content(path, filename, file_data):
    settings = _get_settings()
    bucket = settings.temp_bucket_name
    key = "/".join([path, filename])
    send_file_to_bucket(bucket, key, file_data)

def set_transcoder(path, filename):
    settings = _get_settings()
    pipeline_name = settings.trans_coder_pipeline_name
    private_prefix = settings.private_bucket_sub_folder
    if not pipeline_name:
        return None
    conn = get_trans_coder_conn()
    if conn is None:
        return None
    pipelines = conn.list_pipelines().get(u'Pipelines', [])
    pipeline_id = _get_pipeline_name_to_id(pipelines, pipeline_name)
    if pipeline_id is None:
        pipeline_id = create_new_transcoder_pipeline(conn, pipeline_name)
        if pipeline_id is None:
            return None

    input_file = '/'.join([path, filename])
    input_name = {
        "Key":input_file,
        "FrameRate":"auto",
        "Resolution":"auto",
        "AspectRatio":"auto",
        "Interlaced":"auto",
        "Container":"auto",
        }
    outputs = [
        {'Key': 'video',
         "PresetId": "1351620000001-200050", # HLS (Apple HTTP Live Streaming), 400 kilobits/second
         # http://docs.aws.amazon.com/elastictranscoder/latest/developerguide/system-presets.html
         "SegmentDuration":"10",
         'Rotate': 'auto',
         'ThumbnailPattern': "HLS{count}",
        },
        {'Key': 'video.mp4',
         "PresetId": "1351620000001-000040", # Generic 360p 16:9
         'Rotate': 'auto',
         'ThumbnailPattern': "",
        },
    ]
    output_key_prefix = '/'.join(f for f in [private_prefix, path]
                                    if f) + "/"
    job_dic = conn.create_job(pipeline_id=pipeline_id,
                              input_name=input_name,
                              outputs=outputs,
                              output_key_prefix=output_key_prefix)
    job_id = job_dic.get(u"Job", {}).get(u"Id")
    return job_id

def get_transcoder_status(job_id):
    conn = get_trans_coder_conn()
    job = conn.read_job(id=job_id)
    if not job:
        return None
    return job.get(u"Job", {}).get(u'Status'), job


def get_videos_path():
    settings = _get_settings()
    bucket_name = settings.private_bucket_name
    bucket_obj = get_s3_bucket(bucket_name)
    if bucket_obj is None:
        return []
    prefix = settings.private_bucket_sub_folder
    result = bucket_obj.list(prefix=prefix+"/", delimiter="/")
    return result

def remove_garbage_video_s3(garbage_videos):
    settings = _get_settings()
    bucket_name = settings.private_bucket_name
    bucket_obj = get_s3_bucket(bucket_name)
    result = bucket_obj.delete_keys(garbage_videos)
    return result

def create_s3_bucket(bucket_name, remove_setting=False):
    """return bucket name"""
    bucket_obj = get_s3_bucket(bucket_name)
    if not bucket_obj:
        access_key_id, secret_access_key = get_access_key()
        if access_key_id is None or secret_access_key is None:
            return None
        conn = S3Connection(access_key_id, secret_access_key)
        bucket_obj = conn.create_bucket(bucket_name)
    if bucket_obj:
        if remove_setting:
            lifecycle_config = Lifecycle()
            lifecycle_config.add_rule('remove_setting', '/', 'Enabled', 1)
            bucket_obj.configure_lifecycle(lifecycle_config)
        return bucket_name
    else:
        return None


# def confirem_cloudfront_key(old_key_id, old_key_str):
#     """return True: same key id/ False: need to replace"""
#     cloudfront_key_id, cloudfront_private_key_str = get_cloudfront_keys()
#     if old_key_id == cloudfront_key_id and old_key_str == cloudfront_private_key_str:
#         return True
#     else:
#         return False
#
# def create_cloudfront_key():
#     """return new_cloudfront_key_id, new_cloudfront_private_key_str"""

def create_cloudfront4web():
    """return domain name"""
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    conn = CloudFrontConnection(access_key_id, secret_access_key)
    settings = _get_settings()
    bucket_name = settings.private_bucket_name
    if not bucket_name:
        raise Exception("no bucket_name")
    origin = '%s.s3.amazonaws.com' % bucket_name
    oai_name = "OAI_%s_web_%s" % (bucket_name, str(datetime.now()))
    oai = conn.create_origin_access_identity(comment=oai_name)
    origin_obj = S3Origin(dns_name=origin, origin_access_identity=oai)
    ts = TrustedSigners()
    ts.append('Self')
    distro = conn.create_distribution(origin=origin_obj, enabled=True, cnames=None,
                             comment='', trusted_signers=ts)
    # bucket_obj = get_s3_bucket(bucket_name)
    # bucket_obj.add_user_grant("READ", oai.s3_user_id)
    distro_id = distro.id
    logging_obj = LoggingInfo(bucket=origin, prefix='logs/web/')
    config_obj = conn.get_distribution_config(distro_id)
    config_obj.logging = logging_obj
    config_obj.origin.origin_access_identity = oai
    conn.set_distribution_config(distro_id, etag=config_obj.etag, config=config_obj)
    distro.set_permissions_all(replace=False)
    domain_name = distro.domain_name
    return domain_name

def create_cloudfront4rtmp():
    """return domain name"""
    access_key_id, secret_access_key = get_access_key()
    if access_key_id is None or secret_access_key is None:
        return None
    conn = CloudFrontConnection(access_key_id, secret_access_key)
    settings = _get_settings()
    bucket_name = settings.private_bucket_name
    if not bucket_name:
        raise Exception("no bucket_name")
    origin = '%s.s3.amazonaws.com' % bucket_name
    oai_name = "OAI_%s_rtmp_%s" % (bucket_name, str(datetime.now()))
    oai = conn.create_origin_access_identity(comment=oai_name)
    origin_obj = S3Origin(dns_name=origin, origin_access_identity=oai)
    ts = TrustedSigners()
    ts.append('Self')
    distro = conn.create_streaming_distribution(origin=origin_obj, enabled=True, cnames=None,
                             comment='', trusted_signers=ts)
    # bucket_obj = get_s3_bucket(bucket_name)
    # bucket_obj.add_user_grant("READ", oai.s3_user_id)
    distro_id = distro.id
    logging_obj = LoggingInfo(bucket=origin, prefix='logs/rtmp/')
    config_obj = conn.get_streaming_distribution_config(distro_id)
    config_obj.logging = logging_obj
    config_obj.origin.origin_access_identity = oai
    conn.set_streaming_distribution_config(distro_id, etag=config_obj.etag, config=config_obj)
    distro.set_permissions_all(replace=False)
    domain_name = distro.domain_name
    return domain_name



