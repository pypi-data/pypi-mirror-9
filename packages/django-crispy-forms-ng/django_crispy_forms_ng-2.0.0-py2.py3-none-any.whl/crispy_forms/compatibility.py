try:
    # Try Django's lru_cache (available on Django 1.7+).
    # Should be removed when 1.4 support is dropped.
    from django.utils.lru_cache import lru_cache
except ImportError:
    try:
        # Try Python's version (available on Python 3.2+).
        from lru_cache import lru_cache
    except ImportError:
        # We're on Python 2 with Django < 1.7. (Python 3.0 and 3.1 are not
        # supported by Django.) Fallback to a naive implementation based on
        # memoize.
        from django.utils.functional import memoize

        def lru_cache(maxsize):
            return lambda func: memoize(func, {}, 1)
