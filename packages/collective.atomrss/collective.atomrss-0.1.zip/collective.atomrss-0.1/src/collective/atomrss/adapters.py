from Products.ATContentTypes.interfaces import IATNewsItem
from Products.ATContentTypes.interfaces import IATEvent
from Products.CMFPlone.browser.syndication.adapters import BaseItem
from Products.CMFPlone.browser.syndication.settings import FeedSettings
from Products.CMFPlone.interfaces.syndication import IFeed
from Products.CMFPlone.browser.syndication.settings import FEED_SETTINGS_KEY
from zope.annotation.interfaces import IAnnotations
from zope.component import adapts


class AtomFeedSettings(FeedSettings):
    """ Change default value for feed : atom.xml is first and render_body True
    """

    def __init__(self, context):
        super(AtomFeedSettings, self).__init__(context)
        annotations = IAnnotations(context)

        if 'render_body' not in self._metadata.keys():
            self._metadata['render_body'] = True
            annotations[FEED_SETTINGS_KEY] = self._metadata
        if 'feed_types' not in self._metadata.keys():
            self._metadata['feed_types'] = (u'atom.xml', u'RSS', u'rss.xml')
            annotations[FEED_SETTINGS_KEY] = self._metadata


class NewsFeedItem(BaseItem):
    adapts(IATNewsItem, IFeed)

    @property
    def banner_image_url(self):
        image_field = 'image'
        scaling = 'preview'
        return "{0}/{1}_{2}".format(
            self.context.absolute_url(),
            image_field,
            scaling)


class EventFeedIItem(BaseItem):
    adapts(IATEvent, IFeed)

    @property
    def startdate(self):
        return str(self.context.startDate)

    @property
    def enddate(self):
        return str(self.context.endDate)

    @property
    def contactname(self):
        return self.context.contact_name()

    @property
    def contactemail(self):
        return self.context.contact_email()

    @property
    def contactphone(self):
        return self.context.contact_phone()

    @property
    def location(self):
        return self.context.location

    @property
    def eventurl(self):
        return self.context.event_url()

    @property
    def banner_image_url(self):
        image_field = 'leadImage'
        field = self.context.getField(image_field)
        # Check if there is a leadImage and if it's not empty
        if field is not None:
            value = field.get(self.context)
            if not bool(value):
                return False
        else:
            return False
        scaling = 'preview'
        return "{0}/{1}_{2}".format(
            self.context.absolute_url(),
            image_field,
            scaling)
