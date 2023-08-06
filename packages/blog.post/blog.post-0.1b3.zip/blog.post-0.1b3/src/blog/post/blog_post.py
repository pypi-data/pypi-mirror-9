# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.supermodel import model
from blog.post import _
from plone.namedfile.field import NamedBlobImage
from plone.dexterity.content import Item
from zope.interface import implements
from plone.app.discussion.interfaces import IConversation


class IBlogPost(model.Schema):
    """A blog post. Can add comments on a blog post.
    """

    image = NamedBlobImage(
        title=_(u"Image thumb"),
        description=_(u"If there is an image, it'll be visible for thumb of blog post."),
        required=False,
    )
    text = RichText(
        title=_(u"Text"),
        description=_(u"Blog content"),
        required=False,
    )


class BlogPost(Item):
    implements(IBlogPost)

    def total_comments(self):
        try:
            conversation = IConversation(self)
            return conversation.total_comments
        except TypeError:
            return 0


def created(context, event):
    context.exclude_from_nav = True
