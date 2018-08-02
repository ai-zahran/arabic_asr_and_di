#: Title : transliteration.py
#: Author : "Ahmed Ismail" <ahmed.ismail.zahran@gmail.com>
#: Version : 1.0
#: Description : Functions to perform transliteration on a sentence


# Unicode/Buckwalter dictionary
unicode2buckwalter_dict = {u'\u0621': '\'', u'\u0622': '|', u'\u0623': '>',
    u'\u0624': '&', u'\u0625': '<', u'\u0626': '}', u'\u0627': 'A',
    u'\u0628': 'b', u'\u0629': 'p', u'\u062A': 't', u'\u062B': 'v',
    u'\u062C': 'j', u'\u062D': 'H', u'\u062E': 'x', u'\u062F': 'd',
    u'\u0630': '*', u'\u0631': 'r', u'\u0632': 'z', u'\u0633': 's',
    u'\u0634': '$', u'\u0635': 'S', u'\u0636': 'D', u'\u0637': 'T',
    u'\u0638': 'Z', u'\u0639': 'E', u'\u063A': 'g', u'\u0640': '_',
    u'\u0641': 'f', u'\u0642': 'q', u'\u0643': 'k', u'\u0644': 'l',
    u'\u0645': 'm', u'\u0646': 'n', u'\u0647': 'h', u'\u0648': 'w',
    u'\u0649': 'Y', u'\u064A': 'y', u'\u064B': 'F', u'\u064C': 'N',
    u'\u064D': 'K', u'\u064E': 'a', u'\u064F': 'u', u'\u0650': 'i',
    u'\u0651': '~', u'\u0652': 'o', u'\u0670': '`', u'\u0671': '{',
    ' ': ' '}

buckwalter2unicode_dict = {value: key for key, value in
    unicode2buckwalter_dict.items()}


def transliterate(text, input_format='unicode', output_format='buckwalter',
    ignore_absent=False):
    ''' Transliterates text using the specified mapping

    Arguments
    ---------

    text : String containing the text to transliterate.

    input_format : String describing input text format. Default is 'unicode'.

    output_format : String describing output text format.
    Default is 'buckwalter'.

    ignore_absent : Boolean. if set to True, characters absent from the
    mapping will be ignored in the transliteration. If set to False, absent
    characters will be output without mapping in the transliteration. Default
    is False.

    Returns
    -------

    text : String containing transliterated text.
    '''

    if input_format == output_format:
        return text

    if input_format == 'unicode' and output_format == 'buckwalter':
        mapping = unicode2buckwalter_dict
    elif input_format == 'buckwalter' and output_format == 'unicode':
        mapping = buckwalter2unicode_dict
    else:
        raise Exception('Unknown mapping formats defined.')

    if ignore_absent:
        text = ''.join([mapping[c] if c in mapping else '' for c in text])
    else:
        text = ''.join([mapping[c] if c in mapping else c for c in text])
    return text