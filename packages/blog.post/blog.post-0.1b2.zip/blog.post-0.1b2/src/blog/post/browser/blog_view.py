# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.app.discussion.interfaces import IConversation
from plone import api
from blog.post.browser import utils
from blog.post.blog_post import IBlogPost


class BlogView(BrowserView):
    """Blog View class"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.effdate = self.context.effective_date

    def get_total_comments(self):
        try:
            conversation = IConversation(self.context)
            return conversation.total_comments
        except TypeError:
            return 0

    def get_datetime_human(self):
        if self.effdate:
            return api.portal.get_localized_time(datetime=self.effdate)
        else:
            return False

    def get_author_name(self):
        return utils.get_author_name(self.context)

    def get_author_url(self):
        return utils.get_author_url(self.context)


from zope.component import adapts
from Products.CMFPlone.interfaces.syndication import IFeed
from plone.dexterity.interfaces import IDexterityContent
from Products.CMFPlone.browser.syndication.adapters import DexterityItem


class RssAdapter(DexterityItem):
    adapts(IBlogPost, IFeed)

    @property
    def link(self):
        url = self.context.absolute_url()
        return url

    def author_name(self):
        return utils.get_author_name(self.context)

    @property
    def body(self):
        return self.context.text.output
