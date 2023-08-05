
from zope import schema
from zope.interface import Interface
from zope.interface import implements
# from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from c2.app.streamingaws import StreamingAwsMessageFactory as _


class RegionVocabulary(object):
    """
    """
    implements(IVocabularyFactory)
    def __call__(self, context):
        items =(
(u"elastictranscoder.us-east-1.amazonaws.com", "us-east-1", u"US East (Northern Virginia) Region (us-east-1)"),
(u"elastictranscoder.us-west-1.amazonaws.com", "us-west-1", u"US West (Northern California) Region (us-west-1)"),
(u"elastictranscoder.us-west-2.amazonaws.com", "us-west-2", u"US West (Oregon) Region (us-west-2)"),
(u"elastictranscoder.eu-west-1.amazonaws.com", "eu-west-1", u"EU (Ireland) Region (eu-west-1)"),
(u"elastictranscoder.ap-southeast-1.amazonaws.com", "ap-southeast-1", u"Asia Pacific (Singapore) Region (ap-southeast-1)"),
(u"elastictranscoder.ap-northeast-1.amazonaws.com", "ap-northeast-1", u"Asia Pacific (Tokyo) Region (ap-northeast-1)"),
        )
        return SimpleVocabulary(
            [SimpleTerm(value=r[0], token=r[1], title=r[2])
                    for r in items])

RegionVocabularyFactory= RegionVocabulary()


class IStreamingAwsControlPanel(Interface):
    """IStreaming Aws ControlPanel setting interface
    """

    access_key_id = schema.TextLine(
        required=True,
        title=_(u"ACCESS_KEY_ID"),
        default=u""
        )

    secret_access_key = schema.TextLine(
        required=True,
        title=_(u"SECRET_ACCESS_KEY"),
        default=u""
        )

    region_name = schema.Choice(
        required=True,
        title=_(u"REGION_NAME"),
        description=u"You can choice region of supported Transcoder",
        vocabulary="c2.app.streamingaws.region_select",
        )

    temp_bucket_name = schema.TextLine(
        required=True,
        title=_(u"TEMP_BUCKET_NAME"),
        default=u""
        )

    private_bucket_name = schema.TextLine(
        required=True,
        title=_(u"PRIVATE_BUCKET_NAME"),
        default=u""
        )

    private_bucket_sub_folder = schema.TextLine(
        required=False,
        title=_(u"PRIVATE_BUCKET_SUB_FOLDER"),
        description=u"Sub folder, if you want to use. e.g) sitename/video",
        default=u"",
        )
    trans_coder_pipeline_name = schema.TextLine(
        required=False,
        title=_(u"TRANS_CODER_PIPELINE_NAME"),
        description=u"You should input Pipeline name, if you want to trans code for HLS. \
                If it is blank, does not work transcoder. e.g) SITE_NAME-video",
        default=u"",
        )
    cloudfront_key_id = schema.TextLine(
        required=False,
        title=_(u"CloudFront_KEYPAIR_ID"),
        description=u"",
        default=u"",
        )
    cloudfront_private_key_str =schema.Text(
        required=False,
        title=_(u"CloudFront_PRIVATE_KEY_STRING"),
        description=u"",
        default=u"",
        )
    cloudfront_web_domain = schema.TextLine(
        required=False,
        title=_(u"CloudFront_web_domain"),
        description=u"You don't need to input, because auto putting from 'Setting AWS'\
                HTTP domain for CloudFront. e.g) xxxxxx.cloudfront.net \
                If it is blank, does not work HTTP streaming(HLS).",
        default=u"",
        )
    cloudfront_rtmp_domain = schema.TextLine(
        required=False,
        title=_(u"CloudFront_rtmp_domain"),
        description=u"You don't need to input, because auto putting from 'Setting AWS'\
                RTMP domain for CloudFront. e.g) xxxxxx.cloudfront.net \
                If it is blank, does not work RTMP streaming.",
        default=u"",
        )

