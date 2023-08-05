# coding: utf-8
import uuid
import urllib2
import transaction
from five import grok
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.supermodel import model
from zope import schema
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
import zope.schema.interfaces
from Products.CMFCore.utils import getToolByName
from z3c.form import interfaces
from z3c.form.widget import FieldWidget
from z3c.form.browser.file import FileWidget
from z3c.form.converter import FileUploadDataConverter
# import z3c.form.util
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.directives import dexterity
from plone.directives import form

from c2.app.streamingaws.controlpanel.interfaces import IStreamingAwsControlPanel
from c2.app.streamingaws import StreamingAwsMessageFactory as _
from c2.app.streamingaws.aws_utils import (
                    # send_file_to_bucket_and_copy,
                    send_file_to_bucket_from_content,
                    set_transcoder,
                    get_transcoder_status,
                    get_signed_url)

TRANS_CODER_STATUS_V = SimpleVocabulary(
            [SimpleTerm(value=u"Submitted", token='Submitted', title=u'Submitted'),
            SimpleTerm(value=u"Complete", token='Complete', title=u'Complete'),
            SimpleTerm(value=u"Error", token='Error', title=u'Error'),
            SimpleTerm(value=u"Progressing", token='Progressing', title=u'Progressing'),
            SimpleTerm(value=u"Warning", token='Warning', title=u'Warning'),])

def _to_unicode(s):
    if not isinstance(s, unicode):
        s = s.decode('utf-8')
    return s

def _path_policy_url(path):
    return path.rsplit("/", 1)[0] + "/*"

def sending_aws(path, filename, file_data):
    send_file_to_bucket_from_content(path, filename, file_data)
    # send_file_to_bucket_and_copy(path, filename, file_data) # Don't need copy, because MP4 transcodes too.
    job_id = set_transcoder(path, filename)
    if job_id is not None:
        return job_id
    else:
        return u""

def _adding_param_for_m3u8(data, base_url, signed_param):
    for li in data.split("\n"):
        if not li.strip():
            yield li
        elif li.startswith("#"):
            yield li
        else:
            yield base_url + "/" + li + "?" + signed_param

def get_hls_org_url(context):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IStreamingAwsControlPanel)
    domain = settings.cloudfront_web_domain
    path = context.hls_video
    if not domain or not path:
        return None
    url = "https://" + domain + "/" + path
    return url

def get_mp4_org_url(context):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IStreamingAwsControlPanel)
    domain = settings.cloudfront_rtmp_domain
    path = context.mp4_video
    if not domain or not path:
        return None
    url = "rtmp://" + domain + "/cfx/st/&mp4:" + path
    return url

def get_thumb_org_url(context):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(IStreamingAwsControlPanel)
    domain = settings.cloudfront_web_domain
    path = context.thumbnail_filename
    if not domain or not path:
        return None
    url = "https://" + domain + "/" + path
    return url


class IUploadVideoWidget(interfaces.IFileWidget):
    """
    """

class UploadVideoWidget(FileWidget):
    """
    """
    zope.interface.implementsOnly(IUploadVideoWidget)

    def update(self):
        super(UploadVideoWidget, self).update()

    def extract(self, default=interfaces.NOVALUE):
        file_obj = self.request.get(self.name, default)
        if file_obj and file_obj != default and file_obj.filename:
            return file_obj
        else:
            return None

class FileDataConverter(FileUploadDataConverter):
    """
    """
    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        return None

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""
        if value is None or value == '':
            return interfaces.NOT_CHANGED

        if hasattr(value, 'seek'):
            self.widget.headers = value.headers
            self.widget.filename = value.filename
            try:
                seek = value.seek
                read = value.read
            except AttributeError as e:
                raise ValueError(_('Bytes data are not a file object'), e)
            else:
                seek(0)
                data = read()
                if data or getattr(value, 'filename', ''):
                    path = _to_unicode(uuid.uuid4().hex)
                    org_filename = _to_unicode(value.filename)
                    job_id = sending_aws(path, org_filename, data)
                    # import pdb;pdb.set_trace()
                    transaction.begin()
                    self.widget.context.trans_coder_status = "Submitted"
                    transaction.commit()
                    return {u"path" : path, u"org_filename" : org_filename,
                            u"job_id" : job_id}
                else:
                    return {}
        else:
            return {}


@zope.component.adapter(zope.schema.interfaces.IField, interfaces.IFormLayer)
@zope.interface.implementer(interfaces.IFieldWidget)
def UploadVideoFieldWidget(field, request):
    """IFieldWidget factory for LimitedDateTimeWidget."""
    return FieldWidget(field, UploadVideoWidget(request))

class IStreamingVideo(model.Schema):
    """
    """
    form.widget(video_attr="c2.app.streamingaws.streamingvideo.UploadVideoFieldWidget")
    video_attr = schema.Dict(
        required=False,
        title=_(u"Video file"),
        description=_(u"Video attributes from video file. (.mp4)"),
        key_type = schema.TextLine(title=u"Attribute key"),
        value_type = schema.TextLine(title=u"Attribute value")
        # for job_id, path, original filename
        )
    mp4_video = schema.TextLine(
        required=False,
        title=_(u"Filename of MP4 video"),
        default=u""
        )
    hls_video = schema.TextLine(
        required=False,
        title=_(u"m3u8 filename of hls video"),
        default=u""
        )
    trans_coder_status_message = schema.TextLine(
        required=False,
        title=_(u"Error message of trans coder"),
        default=u""
        )
    thumbnail_filename = schema.TextLine(
        required=False,
        title=_(u"Thumbnail filename"),
        description=u"This field was automatic input from Trans coder. \
                      You can change the field recode, if you want.",
        default=u""
        )
    trans_coder_status = schema.Choice(
        required=True,
        title=_(u'Status of trans coder'),
        default=u"Submitted",
        vocabulary=TRANS_CODER_STATUS_V,
        )

class View(grok.View):
    grok.context(IStreamingVideo)
    grok.require('zope2.View')

    def __call__(self, *args, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IStreamingAwsControlPanel)
        self.trans_coder_status = self.context.trans_coder_status
        if self.trans_coder_status != u"Complete":
            mtool = getToolByName(self.context, "portal_membership")
            user = mtool.getAuthenticatedMember()
            if hasattr(user, "checkPermission") and \
                    user.checkPermission("Modify portal content", self.context):
                transaction.begin()
                self.trans_coder_status = self.update_transcoder_status()
                transaction.commit()
        return super(View, self).__call__(*args, **kwargs)

    def _get_transcoder_job_id(self):
        video_attr = self.context.video_attr
        job_id = video_attr.get("job_id")
        return job_id

    def update_transcoder_status(self):
        job_id = self._get_transcoder_job_id()
        current_status, job_dic = get_transcoder_status(job_id)
        changed = False
        if current_status == u"Submitted":
            pass
        elif current_status == u"Complete":
            changed = True
            video_attr = self.context.video_attr
            if video_attr and video_attr.get("path"):
                settings = self.settings
                path = "/".join(f for f in [
                            settings.private_bucket_sub_folder,
                            video_attr.get("path")] if f)
                if settings.cloudfront_rtmp_domain:
                    self.context.mp4_video = "/".join([path, "video.mp4"])
                if settings.cloudfront_web_domain:
                    self.context.hls_video = "/".join([path, "video.m3u8"])
                if settings.trans_coder_pipeline_name:
                    self.context.thumbnail_filename = "/".join([path, "HLS00001.png"])
        elif current_status == u"Error":
            changed = True
            self.context.trans_coder_status_message = repr(job_dic)
        elif current_status == u"Progressing":
            pass
        elif current_status == u"Warning":
            changed = True
            self.context.trans_coder_status_message = repr(job_dic)
        if changed:
            self.context.trans_coder_status = current_status
            self.context.reindexObject()
        return current_status

    def get_mp4_video(self):
        path = self.context.mp4_video
        url = get_mp4_org_url(self.context)
        if url is None:
            return None
        signed_url = get_signed_url(url, policy_url=_path_policy_url(path))
        return signed_url

    def is_hls_video(self):
        settings = self.settings
        domain = settings.cloudfront_web_domain
        path = self.context.hls_video
        if not domain or not path:
            return False
        else:
            return True

    def get_thumbnail(self):
        url = get_thumb_org_url(self.context)
        if url is None:
            return None
        signed_url = get_signed_url(url, policy_url=_path_policy_url(url))
        return signed_url

class FrameView(View):
    grok.context(IStreamingVideo)
    grok.require('zope2.View')
    grok.name('frame-view')

class InlineTags(grok.View):
    grok.context(IStreamingVideo)
    grok.require('zope2.View')
    grok.name('inline-tags')

    def get_iframe_tag(self):
        iframe_base = u'<iframe width="320" height="180" src="%s" frameborder="0" allowfullscreen></iframe>'
        obj_url = self.context.absolute_url()
        page_id = u"@@frame-view"
        url = obj_url + "/" + page_id
        return iframe_base % url

    def get_hls_uri(self):
        return get_hls_org_url(self.context)

    def get_rtmp_uri(self):
        return get_mp4_org_url(self.context)

    def get_thumb_uri(self):
        return get_thumb_org_url(self.context)

class HLSView(grok.View):
    grok.context(IStreamingVideo)
    grok.require('zope2.View')
    grok.name('m3u8')

    def render(self):
        """
        """
        signed_url = self.get_hls_video()
        if not signed_url:
            return None
        sp_signed_url = signed_url.split("?", 1)
        if len(sp_signed_url) < 2:
            return None
        base_url = sp_signed_url[0].rsplit("/", 1)[0]
        signed_param = sp_signed_url[1]
        m3u8_data = urllib2.urlopen(signed_url)
        data_list = _adding_param_for_m3u8(m3u8_data.read(),
                                           base_url, signed_param)
        m3u8_data.close()
        self.request.RESPONSE.setHeader('Content-Type', 'application/x-mpegURL')
        return "\n".join(data_list)

    def get_hls_video(self):
        url = get_hls_org_url(self.context)
        if url is None:
            return None
        signed_url = get_signed_url(url, policy_url=_path_policy_url(url))
        return signed_url


class AddForm(DefaultAddForm):

    grok.context(IStreamingVideo)

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.fields = self.fields.omit("mp4_video")
        self.fields = self.fields.omit("hls_video")
        self.fields = self.fields.omit("trans_coder_status_message")
        self.fields['trans_coder_status'].mode = interfaces.DISPLAY_MODE

class AddView(DefaultAddView):
    form = AddForm

class StreamingVideoEditForm(dexterity.EditForm):

    grok.context(IStreamingVideo)

    def updateFields(self):
        super(StreamingVideoEditForm, self).updateFields()
        self.fields = self.fields.omit("mp4_video")
        self.fields = self.fields.omit("hls_video")
        self.fields = self.fields.omit("trans_coder_status_message")
        self.fields['trans_coder_status'].mode = interfaces.DISPLAY_MODE
