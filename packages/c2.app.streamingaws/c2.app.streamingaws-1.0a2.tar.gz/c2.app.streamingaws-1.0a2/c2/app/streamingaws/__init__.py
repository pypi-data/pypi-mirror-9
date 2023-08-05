
from zope.i18nmessageid import MessageFactory
StreamingAwsMessageFactory = MessageFactory('c2.app.streamingaws')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
