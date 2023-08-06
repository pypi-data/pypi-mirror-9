from django.contrib import messages
from django.http import HttpResponseServerError, HttpResponseForbidden
from django.template import loader, RequestContext
from ucamwebauth import MalformedResponseError, InvalidResponseError, PublicKeyNotFoundError, UserNotAuthorised, \
    OtherStatusCode


class DefaultErrorBehaviour():
    """ A middleware that catches django-ucamwebauth exceptions and show HTTP 500 or HTTP 403 error messages,
    depending of the error. Furthermore, it uses templates that can be rewritten by a developer.
    """
    def process_exception(self, request, exception):
        if exception.__class__ == MalformedResponseError or \
                exception.__class__ == InvalidResponseError or \
                exception.__class__ == OtherStatusCode or \
                exception.__class__ == PublicKeyNotFoundError:
            template = loader.get_template("ucamwebauth_500.html")
            messages.error(request, str(exception))
            return HttpResponseServerError(template.render(RequestContext(request)))
        elif exception.__class__ == UserNotAuthorised:
            template = loader.get_template("ucamwebauth_403.html")
            messages.error(request, str(exception))
            return HttpResponseForbidden(template.render(RequestContext(request)))
