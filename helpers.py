# Python default packages
import traceback


def exc_to_str(exception: Exception, title: str or None = "EXCEPTION:\n\n", limit: int = 2, separator: str = "") -> str:
    if title is None:
        title = ""
    return title + separator.join(traceback.format_exception(exception, limit=limit))


