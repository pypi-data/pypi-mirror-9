# -*- coding: utf-8 -*-
from plone import api
from plone.app.textfield.value import RichTextValue
lorem_ipsum = u"<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"


def testSetup(context):
    if context.readDataFile('blog.post-testing.txt') is None:
        return
    portal = context.getSite()
    post1 = api.content.create(container=portal, type='blog_post', title='first post')
    post1.text = RichTextValue("<h1>Lorem ipsum</h1>{0}<br/>{0}".format(lorem_ipsum))
    publish(post1)

    collection = api.content.create(container=portal, type='Collection', title='Blog', id='blog')
    query = [
        {'i': 'portal_type',
         'o': 'plone.app.querystring.operation.selection.is',
         'v': ['blog_post']},
        {'i': 'review_state',
         'o': 'plone.app.querystring.operation.selection.is',
         'v': ['published']}
    ]
    collection.setQuery(query)
    collection.setSort_on('created')
    collection.setLayout('blogs_view')
    publish(collection)

    portal.setDefaultPage('blog')


def publish(obj):
    api.content.transition(obj=obj, transition='publish')
    obj.reindexObject()
