try:
    from .loader import releasenotes
except ImportError:
    # Fallback for when imported standalone (e.g., during pytest collection)
    from loader import releasenotes

__all__ = ['releasenotes', ]
