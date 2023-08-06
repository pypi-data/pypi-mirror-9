# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import LogoViewlet


class BlogLogoViewlet(LogoViewlet):

    def update(self):
        super(BlogLogoViewlet, self).update()
        logoName = 'bloglogo.png'
        logoTitle = self.portal_state.portal_title()
        try:
            logo_custom = self.context.restrictedTraverse(logoName)
        except (AttributeError, KeyError):
            # If no custom logo found, super() will handle default one
            pass
        else:
            self.logo_tag = logo_custom.tag(title=logoTitle, alt=logoTitle)
