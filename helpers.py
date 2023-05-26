# Python default packages
import traceback


def exc_to_str(exception: Exception, title: str = "EXCEPTION:\n\n", limit: int = 2, separator: str = "") -> str:
    if title is None:
        title = ""
    return title + separator.join(traceback.format_exception(exception, limit=limit))

def pretify(*args, dec_text: str = '*'):
    results = ()
    for arg in args:
        match type(arg):
            case 'list', 'tuple':
                results += 'list: ' + ', '.join(f'{dec_text}{a}{dec_text} ({type(a)})' for a in arg[:3])
            case 'dict':
                results += ' ; '.join(f"{dec_text}{k}{dec_text} : {dec_text}{v}{dec_text}"
                                      for k, v in arg.items()[:3])
            case _:
                results += f"{dec_text}{arg}{dec_text}"

    return results
