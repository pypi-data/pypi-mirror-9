from zope.component import getMultiAdapter

from plone.app.layout.viewlets.common import ViewletBase

from plone.memoize.view import memoize

from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName


js_template = """
<script type="text/javascript">

    (function($) {
        $(document).ready(function () {
            if($.cookieCuttr) {
                $.cookieCuttr({cookieAnalytics: false,
                               cookieMessage: "%s",
                               cookieAcceptButtonText: "%s"
                               });
                }
        })
    })(jQuery);
</script>

"""


class CookieCuttrViewlet(ViewletBase):

    @memoize
    def language(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        return portal_state.language()

    def update(self):
        pass

    def available(self):
        portal_properties = getToolByName(self.context, 'portal_properties')
        settings = portal_properties.affinitic_simplecookiecuttr
        return getattr(settings, 'enabled', True)

    def index(self):
        if self.available():
            portal_properties = getToolByName(self.context, 'portal_properties')
            settings = portal_properties.affinitic_simplecookiecuttr
            language = self.language()
            text = getattr(settings, 'text_%s' % language, '')
            button = getattr(settings, 'button_%s' % language, '')
            if text and button:
                snippet = safe_unicode(js_template % (text,
                                                      button))
                return snippet
            else:
                from logging import getLogger
                log = getLogger('affinitic.simplecookiecuttr')
                log.info('There are no available %s messages' % language)
        return ""
