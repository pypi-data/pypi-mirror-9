from django.conf import settings
from django.core.urlresolvers import Resolver404
from django.core.urlresolvers import resolve
from django.middleware.csrf import get_token

from app_settings import CLIENT_DATA_NAMESPACE


def client_data(request):
    """
    Put the values in client data into the context.
    The following values are also added:
        * the current user's pk
        * the current user's username
        * the current user's full name
        * the current url's name
        * the current url's arguments
        * the current url's keyword arguments
        * the CSRF token
        * STATIC_URL setting
        * DEBUG setting
    """
    try:
        resolver_match = resolve(request.path_info)
        if resolver_match.namespaces:
            url_name = (':'.join(resolver_match.namespaces) + ':' +
                        resolver_match.url_name)
        else:
            url_name = resolver_match.url_name
        url_args = resolver_match.args
        url_kwargs = resolver_match.kwargs
    except Resolver404:
        url_name = None
        url_args = None
        url_kwargs = None

    if request.user.is_anonymous():
        user_pk = None
        username = None
        full_name = None
    else:
        user_pk = request.user.pk
        username = request.user.username
        full_name = request.user.get_full_name()

    ret = {}
    if request.client_data.include_standard_values:
        standard_values = {
            'user_pk': user_pk,
            'username': username,
            'user_full_name': full_name,
            'url_name': url_name,
            'url_args': url_args,
            'url_kwargs': url_kwargs,
            'csrftoken': get_token(request),
            'STATIC_URL': settings.STATIC_URL,
            'DEBUG': settings.DEBUG,
        }
        ret.update(standard_values)
    ret.update(request.client_data)

    return {
        'CLIENT_DATA_NAMESPACE': CLIENT_DATA_NAMESPACE,
        'client_data': ret,
    }
