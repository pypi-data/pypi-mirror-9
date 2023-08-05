from plone.indexer.decorator import indexer
from five import grok

from c2.app.streamingaws.streamingvideo import IStreamingVideo


@indexer(IStreamingVideo)
def aws_s3_video_path_index(obj):
    """
    """
    d = getattr(obj, "video_attr", None)
    if d is None:
        return None
    return d.get('path')
grok.global_adapter(aws_s3_video_path_index, name="aws_s3_video_path")