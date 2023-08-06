from Cookie import SimpleCookie, CookieError


#=================================================================
class WbUrlBaseCookieRewriter(object):
    """ Base Cookie rewriter for wburl-based requests.
    """
    def __init__(self, url_rewriter):
        self.url_rewriter = url_rewriter

    def rewrite(self, cookie_str, header='Set-Cookie'):
        results = []
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_str)
        except CookieError:
            return results

        for name, morsel in cookie.iteritems():
            morsel = self.rewrite_cookie(name, morsel)
            if morsel:
                results.append((header, morsel.OutputString()))

        return results

    def _remove_age_opts(self, morsel):
        # remove expires as it refers to archived time
        if morsel.get('expires'):
            del morsel['expires']

        # don't use max-age, just expire at end of session
        if morsel.get('max-age'):
            del morsel['max-age']

        # for now, also remove secure to avoid issues when
        # proxying over plain http (TODO: detect https?)
        if morsel.get('secure'):
            del morsel['secure']


#=================================================================
class MinimalScopeCookieRewriter(WbUrlBaseCookieRewriter):
    """
    Attempt to rewrite cookies to minimal scope possible

    If path present, rewrite path to current rewritten url only
    If domain present, remove domain and set to path prefix
    """

    def rewrite_cookie(self, name, morsel):
        # if domain set, no choice but to expand cookie path to root
        if morsel.get('domain'):
            del morsel['domain']
            morsel['path'] = self.url_rewriter.rel_prefix
        # else set cookie to rewritten path
        elif morsel.get('path'):
            morsel['path'] = self.url_rewriter.rewrite(morsel['path'])

        self._remove_age_opts(morsel)
        return morsel


#=================================================================
class ExactPathCookieRewriter(WbUrlBaseCookieRewriter):
    """
    Rewrite cookies only using exact path, useful for live rewrite
    without a timestamp and to minimize cookie pollution

    If path or domain present, simply remove
    """

    def rewrite_cookie(self, name, morsel):
        if morsel.get('domain'):
            del morsel['domain']
        # else set cookie to rewritten path
        if morsel.get('path'):
            del morsel['path']

        self._remove_age_opts(morsel)
        return morsel


#=================================================================
class RootScopeCookieRewriter(WbUrlBaseCookieRewriter):
    """
    Sometimes it is necessary to rewrite cookies to root scope
    in order to work across time boundaries and modifiers

    This rewriter simply sets all cookies to be in the root
    """
    def rewrite_cookie(self, name, morsel):
        # get root path
        morsel['path'] = self.url_rewriter.root_path

        # remove domain
        if morsel.get('domain'):
            del morsel['domain']

        self._remove_age_opts(morsel)
        return morsel


#=================================================================
def get_cookie_rewriter(cookie_scope):
    if cookie_scope == 'root':
        return RootScopeCookieRewriter
    elif cookie_scope == 'exact':
        return ExactPathCookieRewriter
    else:
        return MinimalScopeCookieRewriter
