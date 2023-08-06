# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from blog.post.browser import utils


class BlogsView(BrowserView):
    """Blogs View class for collection or folder"""

    def get_articles(self):
        articles = []
        if self.context.portal_type not in ('Topic', 'Collection'):
            catalog = getToolByName(self.context, 'portal_catalog')
            query = {'portal_type': 'blog_post',
                     'review_state': 'published',
                     'sort_on': 'created',
                     'sort_order': 'descending'}
            query['path'] = {'query': '/'.join(self.context.getPhysicalPath()), 'depth': 3}
            brains = catalog(query)
        else:
            brains = self.context.queryCatalog()
        for brain in brains:
            post = {}
            post['id'] = brain.id
            post['url'] = brain.getURL()
            post['title'] = brain.Title
            post['total_comments'] = brain.total_comments
            blog_post = brain.getObject()
            post['Subject'] = blog_post.Subject()
            post['text'] = blog_post.text.output
            post['author_name'] = utils.get_author_name(blog_post)
            post['author_url'] = utils.get_author_url(blog_post)
            post['human_date'] = utils.get_humain_time(blog_post)
            post['date'] = brain.effective_date
            post['picture'] = blog_post.image

            articles.append(post)

        return articles

    @property
    def truncate(self):
        return 1000

