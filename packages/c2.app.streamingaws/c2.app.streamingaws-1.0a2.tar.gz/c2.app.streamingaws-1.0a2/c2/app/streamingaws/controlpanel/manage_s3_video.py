# cording: utf-8

# from Acquisition import aq_inner
# from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import boto.s3.prefix
from c2.app.streamingaws.controlpanel.interfaces import IStreamingAwsControlPanel
from c2.app.streamingaws.aws_utils import remove_garbage_video_s3, get_videos_path

def _get_s3_full_path(s3_folder, s3_path):
    if s3_path is None:
        return ""
    if s3_folder:
        s3_full_path = s3_folder + "/" + s3_path + "/"
    else:
        s3_full_path = s3_path + "/"
    return s3_full_path

class IManageS3VideoPanel(ISiteRoot):
    """
    """

class ManageS3VideoPanel(BrowserView):
    implements(IManageS3VideoPanel)

    index = ViewPageTemplateFile('manage_s3_video.pt')

    def __call__(self):
        if self.request.form.get('remove.flag') == '1':
            garbage_videos = self.request.form.get('garbage_videos')
            print garbage_videos
            result = remove_garbage_video_s3(garbage_videos)
            print result.deleted
            print result.errors
        return self.index()

    def get_videos(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IStreamingAwsControlPanel)
        s3_folder = settings.private_bucket_sub_folder
        in_plone = self._get_videos_in_plone()
        in_s3 = {key.name for key in self._get_videos_in_s3()}
        for plone_item in in_plone:
            s3_path = plone_item.aws_s3_video_path
            s3_full_path = _get_s3_full_path(s3_folder, s3_path)
            try:
                in_s3.remove(s3_full_path)
            except KeyError:
                s3_full_path = ""
            yield {"in_plone": plone_item.Title + ":" + plone_item.getPath(),
                   "s3_path": s3_full_path,}
        for garbage_obj_path in in_s3:
            # import pdb;pdb.set_trace()
            if not isinstance(garbage_obj_path, boto.s3.prefix.Prefix):
                yield {"in_plone": "",
                       "s3_path": garbage_obj_path,}

    def _get_videos_in_plone(self):
        catalog = getToolByName(self.context, "portal_catalog")
        items = catalog(portal_type="streamingvideo", sort_on="Date")
        return items

    def _get_videos_in_s3(self):
        videos_path = get_videos_path()
        return videos_path