import unicodedata, string, re

from hangups import ChatMessageSegment


def text_to_segments(text):
    """Create list of message segments from text"""
    return ChatMessageSegment.from_str(text)


def unicode_to_ascii(text):
    """Transliterate unicode characters to ASCII"""
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()


def word_in_text(word, text):
    """Return True if word is in text"""
    word = unicode_to_ascii(word).lower()
    text = unicode_to_ascii(text).lower()

    # Replace delimiters in text with whitespace
    for delim in '.,:;!?':
        text = text.replace(delim, ' ')

    return True if word in text.split() else False


def strip_quotes(text):
    """Strip quotes and whitespace at the beginning and end of text"""
    return text.strip(string.whitespace + '\'"')

def contain_number(word):
    return any(i.isdigit() for i in word)

def get_word_with_number(text):
    for word in text.split():
        if contain_number(word) == True: return word
    return ''

def get_url(text):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    return ''.join(urls)

def get_emails(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))
    return (email[0] for email in re.findall(regex, s) if not email[0].startswith('//'))
