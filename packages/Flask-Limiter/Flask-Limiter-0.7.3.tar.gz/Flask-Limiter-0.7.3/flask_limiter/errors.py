"""
errors and exceptions
"""

from distutils.version import LooseVersion
from werkzeug.exceptions import HTTPException

def _patch_werkzeug():
    import pkg_resources
    werkzeug_version = pkg_resources.get_distribution("werkzeug").version
    if LooseVersion(werkzeug_version) < LooseVersion("0.9"):
        # sorry, for touching your internals :).
        import werkzeug._internal # pragma: no cover
        werkzeug._internal.HTTP_STATUS_CODES[429] = 'Too Many Requests' # pragma: no cover

_patch_werkzeug()
del _patch_werkzeug

class RateLimitExceeded(HTTPException):
    """
    exception raised when a rate limit is hit.
    The exception results in ``abort(429)`` being called.
    """
    code = 429
    def __init__(self, limit):
        self.description = str(limit)
        super(RateLimitExceeded, self).__init__()
