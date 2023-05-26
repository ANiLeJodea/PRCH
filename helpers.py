# Python default packages
import traceback


def exc_to_str(exception: Exception, title: str = "EXCEPTION:\n\n", limit: int = 2, separator: str = "") -> str:
    if title is None:
        title = ""
    return title + separator.join(traceback.format_exception(exception, limit=limit))

def pretify(arg, dec_text: str = '*'):
    t = type(arg)
    if t in [list, tuple]:
        return 'list: ' + ', '.join(f'{dec_text}{a}{dec_text} ({type(a)})' for a in arg[:3])
    elif t == "dict":
        return 'dict::' + ' ; '.join(f"{dec_text}{k}{dec_text} : {dec_text}{v}{dec_text}"
                                     for k, v in arg.items()[:3])
    else:
        return f"{dec_text}{arg}{dec_text}"

