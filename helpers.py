# Python default packages
import traceback


def exc_to_str(exception: Exception, title: str = "EXCEPTION:\n\n", limit: int = 2, separator: str = "") -> str:
    if title is None:
        title = ""
    return title + separator.join(traceback.format_exception(exception, limit=limit))

def pretify(arg, dec_text_start: str = '<strong>', dec_text_end: str = '</strong>'):
    t = type(arg)
    if t in [list, tuple]:
        return 'list:: ' + ' ; '.join(f'''{dec_text_start}{a}{dec_text_end} ({str(type(a)).split("'")[1]})''' for a in arg[:3])
    elif t == "dict":
        return 'dict:: ' + ' ; '.join(f"""{dec_text_start}{k}{dec_text_end} : {dec_text_start}{v}{dec_text_end} 
        ({str(type(v)).split("'")[1]})"""
                                      for k, v in arg.items()[:3])
    else:
        return f"{dec_text_start}{arg}{dec_text_end}"

