
from zope.component import getUtility
from z3c.form import interfaces as z3cinterfaces
from plone.app.registry.browser import controlpanel
from plone.registry.interfaces import IRegistry
from plone.registry.interfaces import IRecordModifiedEvent
from Products.CMFCore.utils import getToolByName

from c2.app.streamingaws.controlpanel.interfaces import IStreamingAwsControlPanel
from c2.app.streamingaws import StreamingAwsMessageFactory as _

class StreamingAwsEditForm(controlpanel.RegistryEditForm):

    schema = IStreamingAwsControlPanel
    label = _(u"Streaming AWS settings")

    def updateFields(self):
        super(StreamingAwsEditForm, self).updateFields()

    def updateWidgets(self):
        super(StreamingAwsEditForm, self).updateWidgets()
        self.widgets['cloudfront_private_key_str'].addClass('long-input-textarea')
        # self.widgets['cloudfront_key_id'].mode = z3cinterfaces.DISPLAY_MODE
        # self.widgets['cloudfront_private_key_str'].mode = z3cinterfaces.DISPLAY_MODE

        # For delete
        # self.widgets['cloudfront_web_domain'].mode = z3cinterfaces.DISPLAY_MODE
        # self.widgets['cloudfront_rtmp_domain'].mode = z3cinterfaces.DISPLAY_MODE

    @property
    def description(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        here_url = portal_url + "/@@aws-s3-cloudfront-settings"
        return _(u'''If you did NOT set S3 and CloudFront on AWS,
                you need to click the link: <a href="%s">Setting AWS</a>''' % (here_url,))


class StreamingAwsControlPanel(controlpanel.ControlPanelFormWrapper):
    form = StreamingAwsEditForm


