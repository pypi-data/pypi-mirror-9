class WidgyViewMixin(object):
    site = None

    def auth(self, request, *args, **kwargs):
        self.site.authorize_view(request, self)


class AuthorizedMixin(WidgyViewMixin):
    """
    Makes sure to call auth before doing anything.

    This class should not be used by RestView subclasses.  RestView already
    makes the call to auth, but conveniently wraps the errors to return them in
    JSON-encoded responses.
    """
    def dispatch(self, *args, **kwargs):
        self.auth(*args, **kwargs)
        return super(AuthorizedMixin, self).dispatch(*args, **kwargs)
