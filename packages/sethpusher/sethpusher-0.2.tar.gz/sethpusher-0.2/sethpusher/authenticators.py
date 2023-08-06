import logging


class BaseAuthenticationPolicy(object):

    def authenticate(self, request, **kwargs):
        return True


class EchoAuthenticationPolicy(BaseAuthenticationPolicy):

    def authenticate(self, request, **kwargs):
        logging.debug(u"Dummy Authentication. Skipping ...")
        return True


class ApiKeyAuthenticationPolicy(BaseAuthenticationPolicy):
    key_name = u'api_key'
    key_secret_value = u'secret'

    def authenticate(self, request, **kwargs):
        api_key = request.arguments.get(self.key_name, None)
        if not api_key:
            api_key = request.body_arguments.get(self.key_name, None)

        if not api_key:
            return False

        api_key = api_key[0] if isinstance(api_key, list) else api_key

        return api_key == self.key_secret_value


class HeaderAuthenticationPolicy(BaseAuthenticationPolicy):
    secret_header = u'Seth-Authentication-Header'
    secret_header_value = u'Seth-Value'

    def authenticate(self, request, **kwargs):
        header = request.headers.get(self.secret_header, u'')
        if not header:
            return False

        return header == self.secret_header_value