# Python default packages
import traceback

def exc_to_str(
        exc: Exception, title: str = "EXCEPTION:\n\n",
        limit: int = 2, separator: str = "", chain: bool = False
) -> str:
    return title + separator.join(
        traceback.format_exception(
            type(exc), exc, exc.__traceback__,
            limit=limit, chain=chain
        ))

def form_an_output(
        raw_output: str, num_parts: int, separator: str = '\n', split_by: str = ';'
):
    return separator.join(t for t in raw_output.split(split_by)[:num_parts] if t)

def prettify(arg, dec_start: str = '<strong>', dec_end: str = '</strong>', number_to_show: int = 3):
    t = type(arg)
    if t in [list, tuple]:
        return f'''{number_to_show} first:\n{str(t).split("'")[1]} : ''' + ' ; '.join(
            f'''{dec_start}{a}{dec_end} ({str(type(a)).split("'")[1]})'''
            for a in arg[:number_to_show])
    elif t == dict:
        return f'''{number_to_show} first:\n{str(t).split("'")[1]} : ''' + ' ; '.join(
            f"""{dec_start}{k}{dec_end} : {dec_start}{v}{dec_end} ({str(type(v)).split("'")[1]})"""
            for k, v in arg.items()[:number_to_show])

    return f"{dec_start}{arg}{dec_end}"

def data_to_str(
        data: dict, mode: str = 'html', separator: str = """

"""
):
    mode = mode if mode in ['html', 'markdown'] else 'html'
    dec_text_start, dec_text_end = ('<strong>', '</strong>') if mode == 'html' else ('**', '**')
    return "ALL DATA:\n\n" + \
        separator.join(
            "{}{}{} :: {}".format(dec_text_start, key, dec_text_end, prettify(data, dec_text_start, dec_text_end))
            for key, data in data.items()
        )
