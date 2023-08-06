"""
Utility methods for generating passphrases from a dictionary file of words.
"""

__version_info__ = (0, 7, 0)
__version__ = '.'.join(map(str, __version_info__))

import random
import re
import unicodedata

# python 2/3 compatibility workarounds
try:
    unicode
except NameError:
    u = lambda s: s
    u_type = str
else:
    # default encoding is always supposed to be ascii under python2, so we
    # just try as utf-8 and don't support other encodings for now
    u = lambda s: unicode(s, encoding='utf-8')
    u_type = unicode

try:
    from itertools import imap
except ImportError:
    imap = map


# defaults
MIN = 3        # min word length
MAX = 7        # max word length
WORDS = 4      # num words
PAD = ''       # prefix/suffix of passphrase
DELIM = u(' ')  # delimiter
WORD_FILE = '/usr/share/dict/words'


class EncodingError(Exception):

    """
    Represents an encoding error due to incompatibility between the expected
    and actual encoding of a word read from a word file.
    """


def is_unicode_letter(char):
    """ Answer whether given unicode character is a letter."""
    return unicodedata.category(char) in ('Ll', 'Lu')


def mk_word_matcher(min=MIN, max=MAX, ascii=True):
    """
    Make a word matcher function that accepts a word and returns
    True or False depending on whether the word satisfies the
    the constraints represented by the params.
    :params:
     - min: minimum length of a word
     - max: maximum length of a word
     - ascii: whether to match words that contain only ascii letters
              or words that contain only unicode letters (according to
              ``unicodedata.category``).
    """
    if max < min:
        msg = "min '%s' should be less than or equal to max '%s'"
        raise ValueError(msg % (min, max))
    if ascii:
        pat = re.compile('^[a-zA-Z]{%s,%s}$' % (min, max))

        def matcher(word):
            return bool(pat.match(word))
    else:

        def matcher(word):
            if not isinstance(word, u_type):
                msg = ("Expected unicode words for ascii=False, but found "
                       "word %r of type %s")
                raise EncodingError(msg % (word, type(word)))
            length = len(word)
            return bool(length >= min and length <= max and
                        all(imap(is_unicode_letter, word)))
    return matcher


def get_words(path, min=MIN, max=MAX, ascii=True):
    """
    Get sorted unique words with case normalized to lowercase from file at
    given ``path``, filtering out words that are shorter than ``min`` or longer
    than ``max``. If ``ascii`` is true (default), then only words containing
    just ascii letters are returned. If ``ascii`` is false (and the python
    installation has an appropriate default encoding for the given word file),
    then words in the file that contain only unicode letters (according to
    ``unicodedata.category``) will be included.
    """
    matcher = mk_word_matcher(min=min, max=max, ascii=ascii)
    with open(path) as f:
        words = (line.strip().lower() for line in f)
        if not ascii:
            words = (u(w) for w in words)
        words = list(filter(matcher, set(words)))
    words.sort()
    return words


def sample_words(all_words, k, delim=DELIM, random_case=True):
    """
    Sample ``k`` words from the ``all_words`` word sequence, using ``delim``
    to join the words.

    If ``random_case`` is true (the default), then each word will
    with probability 0.5 be converted to title case.
    """
    all_words = list(all_words)
    words = random.sample(all_words, k)
    if random_case:
        for i, word in enumerate(words):
            if random.choice((True, False)):
                words[i] = word.title()
    return delim.join(words)


def mkpassphrase(path=WORD_FILE, min=MIN, max=MAX, num_words=WORDS,
                 lowercase=False, ascii=True, delim=DELIM, pad=PAD):
    """
    Make a passphrase using given params.

    :params:
    - path: path to a word file, one word per line, encoded with a character
            encoding that is compatible with the python default encoding if
            ``ascii`` is true.
    - min: minimum length of each word in passphrase (at least 1, not greater
           than ``max``).
    - max: maximum length of each word in passphrase (at least 1, not less than
           ``min``).
    - num_words: number of words to include in passphrase (at least 1).
    - lowercase: whether to keep initial letter of each word lowercased or
                 capitalize it with probability 0.5.
    - ascii: whether to only include words contain just ascii letters, or to
             also include words that contain any unicode letter (but no
             characters that are not unicode letters).
    - delim: the delimiter to use for joining the words in the passphrase.
    - pad: a string to use as a prefix and suffix of the generated passphrase.

    :return:
    - passphrase: the generated passphrase (string)
    - num_candidates: the number of unique candidate words used to generate
      the passphrase (int)
    """
    if min < 1:
        raise ValueError("'min' must be at least 1")
    if max < 1 or max < min:
        raise ValueError("'max' must be positive and greater than"
                         " or equal to 'min'")
    if num_words < 1:
        raise ValueError("'num_words' must be at least 1")

    all_words = get_words(path, min=min, max=max, ascii=ascii)
    passphrase = sample_words(all_words, num_words, delim=delim,
                              random_case=not lowercase)
    passphrase = pad + passphrase + pad
    num_candidates = len(all_words)
    if not lowercase:
        num_candidates *= 2
    return passphrase, num_candidates


def num_possible(num_candidates, num_words):
    """
    Calculate the number of possible passphrases that could be generated
    by selecting ``num_words`` from ``num_candidates``, each of which
    must be at least 1.
    """
    if num_candidates < 1:
        raise ValueError('num_candidates must be positive')
    if num_words < 1:
        raise ValueError('num_words must be positive')

    n, k = num_candidates, num_words
    possible = 1
    while k > 0:
        possible *= n
        n -= 1
        k -= 1
    return possible
