"""Holds the logic to  create HTTP requests.

For now we consider HTTP requests as having four components i.e.
 - URL
 - verb
 - params
 - data
"""

class Verbs(object):
    """Represent the most common HTTP verbs."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"

    def __iter__(self):
        """Also test like: 'GET' in Verbs()."""
        for verb in [self.GET, self.POST, self.PUT, self.DELETE]:
            yield verb

VERBS = Verbs()


class Request(object):
    """Represent a HTTP request with a URL, a verb, params and data.

    The idea is to be able to chain calls to methods in order to update each
    components of the Request and put it together before sending it.
    Methods to update the request's components are chainable.

    Example:
    Code  req= | top_resource(12)  | .update_sub_resource(42)| .name("popo")
    URL   "/"  | "/top_resource/12"|   +="/sub_resource/42"  |  +="/"
    VERB  "GET"| "GET"             |   "PUT"                 |  "PUT"
    PARAMS {}  | {}                |   {}                    |  {}
    DATA   {}  | {}                |   {}                    |  {"name":"popo"}

    req.execute() # or something equivalent
    """

    def __init__(self):
        """Initialize components of the HTTP requests to its default value."""
        self._url = ""
        self._verb = VERBS.GET
        self._params = {}
        self._data = {}

    @property
    def url(self):
        """Alias private attribute url."""
        return self._url

    @property
    def verb(self):
        """Alias private attribute verb."""
        return self._verb

    @property
    def params(self):
        """Alias private attribute params."""
        return self._params

    @property
    def data(self):
        """Alias private attribute data."""
        return self._data

    @verb.setter
    def verb(self, verb):
        """Enforce that the verb is known, raises a ValueError otherwise."""
        if verb not in VERBS:
            raise ValueError("Unkown HTTP verb '%s'" % verb)
        self._verb = verb

    def update_verb(self, verb):
        """Update the request verb with the given verb."""
        self.verb = verb
        return self

    def update_params(self, extra_params):
        """Update parameters with given dict, existing key are overwritten."""
        self._params.update(extra_params)
        return self

    def update_url(self, path):
        """Concatenate given path to existing url."""
        self._url += "/%s" % path.lstrip("/")
        return self

    def update_data(self, extra_data):
        """Update data with given dict, existing key are overwritten."""
        self._data.update(extra_data)
        return self

