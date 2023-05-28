# Python default packages
import traceback


def exc_to_str(
        exc: Exception, title: str = "EXCEPTION:\n\n",
        limit: int = 2, separator: str = "", chain: bool = False
) -> str:
    if title is None:
        title = ""
    return title + separator.join(traceback.format_exception(
        type(exc), exc, exc.__traceback__,
        limit=limit, chain=chain))

def pretify(arg, dec_start: str = '<strong>', dec_end: str = '</strong>'):
    t = type(arg)
    if t in [list, tuple]:
        return f'''\n{str(t).split("'")[1]} : ''' + ' ; '.join(
            f'''{dec_start}{a}{dec_end} ({str(type(a)).split("'")[1]})'''
            for a in arg[:3])
    elif t == dict:
        return f'''{str(t).split("'")[1]} : ''' + ' ; '.join(
            f"""{dec_start}{k}{dec_end} : {dec_start}{v}{dec_end} ({str(type(v)).split("'")[1]})"""
            for k, v in arg.items()[:3])
    else:
        return f"{dec_start}{arg}{dec_end}"

