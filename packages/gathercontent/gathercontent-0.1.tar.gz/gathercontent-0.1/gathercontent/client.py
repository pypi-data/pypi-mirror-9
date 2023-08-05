import requests
from requests.auth import HTTPDigestAuth


class GatherContent():
    """
    This is a wrapper around the GatherContent JSON API.
    https://help.gathercontent.com/developer-api/
    """

    base_uri = "https://%s.gathercontent.com/%s"
    base_path = "api/0.4"

    def __init__(self, account_name, api_key, host=False, base_path=False, password="x"):
        """
        Set a few required authentication bits, and optional config.
        The default password is 'x', which is a bit of a WTF. That's 
        the official way to do this though.
        """

        # Account name, API key and password.
        self.account_name = account_name
        self.api_key = api_key
        self.password = password

        # Hostname and path. These probably don't change often, but why not make it configurable.
        if host:
            self.host = host

        if base_path:
            self.base_path = base_path

        # Interpolate the base URI.
        self.base_uri = self.base_uri % (self.account_name, self.base_path)

    def __getattr__(self, name):
        """
        Overload __getattr__() to intercept and 'get_' calls, and map
        them on to API requests.
        """

        # Check the prefix on the requested attribute.
        if name.startswith('get_'):
            # Make the right API request.
            def func(*args, **kwargs):
                return self.request(name, *args, **kwargs)

            return func

        # Default to standard getattr.
        return getattr(self, name)

    def build_auth(self):
        """
        Creates the requests.HTTPDigestAuth object.
        """

        return HTTPDigestAuth(self.api_key, self.password)

    def request(self, uri, **kwargs):
        """
        Creates, POSTs, and returns the JSON from the request.
        """

        response = requests.post("%s/%s" % (self.base_uri, uri), auth=self.build_auth(), data=kwargs)
        return response.json()
