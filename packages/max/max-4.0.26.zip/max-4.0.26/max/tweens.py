# -*- coding: utf-8 -*-
from max.exceptions import JSONHTTPPreconditionFailed


def compatibility_checker_factory(handler, registry):
    def compatibility_checker_tween(request):
        requested_compat_id = request.headers.get('X-Max-Compat-ID', None)
        if requested_compat_id is None:
            response = handler(request)
            return response

        expected_compat_id = str(request.registry.settings.get('max.compat_id'))
        if expected_compat_id == requested_compat_id:
            response = handler(request)
            return response
        else:
            return JSONHTTPPreconditionFailed(
                error=dict(
                    objectType='error',
                    error="CompatibilityIDMismatch",
                    error_description='X-Max-Compat-ID header value mismatch, {} was expected'.format(expected_compat_id)))
    return compatibility_checker_tween


def post_tunneling_factory(handler, registry):
    def post_tunneling_tween(request):
        original_body = request.body
        # Look for header in post-data if not found in headers
        overriden_method = request.headers.get('X-HTTP-Method-Override', request.params.get('X-HTTP-Method-Override', None))
        is_valid_overriden_method = overriden_method in ['DELETE', 'PUT', 'GET']
        is_POST_request = request.method.upper() == 'POST'
        if is_POST_request and is_valid_overriden_method:
            # If it's an overriden GET pass over the authentication data in the post body
            # to the headers, before overriding the method, after this, post data will be lost
            if overriden_method == 'GET':
                request.headers.setdefault('X-Oauth-Token', request.params.get('X-Oauth-Token', ''))
                request.headers.setdefault('X-Oauth-Username', request.params.get('X-Oauth-Username', ''))
                request.headers.setdefault('X-Oauth-Scope', request.params.get('X-Oauth-Scope', ''))

            request.method = overriden_method

        # Restore uncorrupted body
        request.body = original_body
        response = handler(request)
        return response
    return post_tunneling_tween


def browser_debug_factory(handler, registry):
    def browser_debug_tween(request):
        debug = request.params.get('d', None)
        debugging = debug is not None
        if debugging:
            user = request.params.get('u', None)
            token = request.params.get('t', 'fake_token')
            method = request.params.get('m', '').upper()
            payload = request.params.get('p', None)

            if user:
                new_headers = {
                    'X-Oauth-Token': token,
                    'X-Oauth-Username': user,
                    'X-Oauth-Scope': 'widgetcli'
                }
                request.headers.update(new_headers)

                if method in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                    request.method = method.upper()

                if payload:
                    request.text = payload

        response = handler(request)

        if debug == '1' and user:
            response.content_type = 'text/html'
            response.text = u'<html><body>{}</body></html>'.format(response.text)
        return response

    return browser_debug_tween
