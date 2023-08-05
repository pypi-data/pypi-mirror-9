# coding: utf-8

import urllib2
import urllib
import urlparse
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from c2.app.streamingaws.controlpanel.interfaces import IStreamingAwsControlPanel
from c2.app.streamingaws.aws_utils import (create_s3_bucket,
                                           # confirem_cloudfront_key,
                                           # create_cloudfront_key,
                                           create_cloudfront4web,
                                           create_cloudfront4rtmp,)


class ManageAwsSettings(BrowserView):
    """
    """

    def __call__(self):
        portal_messages = IStatusMessage(self.request)
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IStreamingAwsControlPanel)
        access_key_id = settings.access_key_id
        secret_access_key = settings.secret_access_key
        region_name = settings.region_name
        temp_bucket_name = settings.temp_bucket_name
        private_bucket_name = settings.private_bucket_name
        trans_coder_pipeline_name = settings.trans_coder_pipeline_name
        cloudfront_web_domain = settings.cloudfront_web_domain
        cloudfront_rtmp_domain = settings.cloudfront_rtmp_domain

        if not access_key_id or not secret_access_key or not region_name or\
                not temp_bucket_name or not private_bucket_name:
            portal_messages.add(u"Cloud not setting, because no input to need forms",
                                type=u"error")
            return self.request.RESPONSE.redirect("@@streaming-aws-settings")

        temp_bucket = create_s3_bucket(temp_bucket_name, remove_setting=True)
        private_bucket = create_s3_bucket(private_bucket_name)
        # cloudfront_key_id = settings.cloudfront_key_id
        # cloudfront_private_key_str = settings.cloudfront_private_key_str
        # if cloudfront_key_id and cloudfront_private_key_str:
        #     chk_key = confirem_cloudfront_key(cloudfront_key_id,
        #                                       cloudfront_private_key_str)
        # else:
        #     chk_key = False
        # if chk_key:
        #     new_cloudfront_key_id, new_cloudfront_private_key_str = create_cloudfront_key()
        #     settings.cloudfront_key_id = new_cloudfront_key_id
        #     settings.cloudfront_private_key_str = new_cloudfront_private_key_str
        if trans_coder_pipeline_name and not cloudfront_web_domain:
            new_cloudfront_web_domain = create_cloudfront4web()
            if new_cloudfront_web_domain:
                settings.cloudfront_web_domain = new_cloudfront_web_domain
        if not cloudfront_rtmp_domain:
            new_cloudfront_rtmp_domain = create_cloudfront4rtmp()
            if new_cloudfront_rtmp_domain:
                settings.cloudfront_rtmp_domain = new_cloudfront_rtmp_domain

        portal_messages.add(u"Setting S3 and CloudFront on AWS", type=u"info")
        return self.request.RESPONSE.redirect("@@streaming-aws-settings")


