# -*- coding: utf-8 -*-
import re
import unicodedata

from Products.ZCTextIndex.ISplitter import ISplitter
from Products.ZCTextIndex.PipelineFactory import element_factory

# STOP_WORDS = ('*','?')
ENC = "utf-8"

RE_WORD = re.compile(r"\w+", re.UNICODE)
RE_GLOB_WORD = re.compile(r"\w+[\w*?]*", re.UNICODE)

def bigram(u, limit=1):
    """ Split into bi-gram.
    limit arg describes ending process.
    If limit = 0 then
        日本人-> [日本,本人, 人]
        金 -> [金]
    If limit = 1 then
        日本人-> [日本,本人]
        金 -> []
    """
    return [u[i:i+2] for i in xrange(len(u) - limit)]

def process_unicode(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    for word in RE_WORD.findall(normalized):
        for x in bigram(word, 0):
            yield x

def process_unicode_glob(uni):
    """Receive unicode string, then return a list of unicode
    as bi-grammed result.  Considering globbing.
    """
    normalized = unicodedata.normalize('NFKC', uni)
    words = [word for word in RE_GLOB_WORD.findall(normalized)
                    if word not in u"*?"]
    len_words = len(words)
    for i, word in enumerate(words):
        if i == len_words - 1:
            limit = 1
        else:
            limit = 0
        if len(word) == 1:
            bigramed = [word + u"*"]
        else:
            bigramed = bigram(word, limit)
        for x in bigramed:
            yield x

def process_str(s, enc):
    """Receive str and encoding, then return the list
    of str as bi-grammed result.
    Decode str into unicode and pass it to process_unicode.
    When decode failed, return the result splitted per word.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError, e:
        uni = s.decode(enc, "replace")
    bigrams = process_unicode(uni)
    return [x.encode(enc, "strict") for x in bigrams]

def process_str_glob(s, enc):
    """Receive str and encoding, then return the list
    of str considering glob processing.
    Decode str into unicode and pass it to process_unicode_glob.
    When decode failed, return the result splitted per word.
    Splitting depends on locale specified by rxGlob_L.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError, e:
        uni = s.decode(enc, "replace")
    bigrams = process_unicode_glob(uni)
    return [x.encode(enc, "strict") for x in bigrams]

def process_str_post(s, enc):
    """Receive str, remove ? and *, then return str.
    If decode gets successful, process str as unicode.
    If decode gets failed, process str as ASCII.
    """
    try:
        if not isinstance(s, unicode):
            uni = s.decode(enc, "strict")
        else:
            uni = s
    except UnicodeDecodeError, e:
        return s.replace("?", "").replace("*", "")
    try:
        return uni.replace(u"?", u"").replace(u"*", u"").encode(enc, "strict")
    except UnicodeEncodeError, e:
        return s.replace("?", "").replace("*", "")


class C2TwoCharaSplitter(object):
    """
    2 character Splitter
    """
    __implements__ = ISplitter

    def process(self, lst):
        """ Will be called when indexing.
        Receive list of str, make it bi-grammed, then return
        the list of str.
        """
        result = [x for s in lst for x in process_str(s, ENC)]
        return result

    def processGlob(self, lst):
        """ Will be called once when searching.
        Receive list of str, make it bi-grammed considering
        globbing, then return the list of str.
        """
        result = [x for s in lst for x in process_str_glob(s, ENC)]
        return result

    def process_post_glob(self, lst):
        """ Will be called twice when searching.
        Receive list of str, Remove ? and *, then return
        the list of str.
        """
        result = [process_str_post(s, ENC) for s in lst]
        return result

element_factory.registerFactory('Word Splitter',
                        'C2TwoCharaSplitter', C2TwoCharaSplitter)

class C2TwoCharaNormalizer(object):

    def process(self, lst):
        result = []
        for s in lst:
            # This is a hack to get the normalizer working with
            # non-unicode text.
            try:
                if not isinstance(s, unicode):
                    s = unicode(s, ENC)
            except (UnicodeDecodeError, TypeError):
                result.append(s.lower())
            else:
                normalized = unicodedata.normalize('NFKC', s)
                result.append(normalized.lower().encode(ENC))
        return result

element_factory.registerFactory('Case Normalizer',
        'C2TwoChara Case Normalizer', C2TwoCharaNormalizer)