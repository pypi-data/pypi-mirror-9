# -*- coding: utf-8 -*-
from plone import api
from plone.app.discussion.interfaces import IConversation


def get_author_name(context):
    username = context.Creator()
    user = api.user.get(username=username)
    name = user.getProperty('fullname')
    if name:
        return name
    else:
        return username


def get_author_url(context):
    username = context.Creator()
    return username


def get_humain_time(context):
    if context.effective_date:
        return api.portal.get_localized_time(datetime=context.effective_date)
    else:
        return False
