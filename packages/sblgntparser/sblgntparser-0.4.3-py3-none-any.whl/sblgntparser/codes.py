import logging
log = logging.getLogger(__name__)

class Code():
    '''
    All codes are derived from `http://jtauber.com/2010/07/parse-helper/demo.html`
    '''
    def __init__(self, codes, name):
        self.codes = codes
        self.name = name

    def get(self, code):
        clow = code.lower()
        if clow in self.codes:
            return self.codes[clow]
        elif code is '-':
            pass
        else:
            log.warn('Unknown {} code: "{}"'.format(self.name, code))

def person(code):
    p = Code({
        '1': '1st person',
        '2': '2nd person',
        '3': '3rd person'
        }, 'person')
    return p.get(code)

def tense(code):
    t = Code({
        "p" : "present",
        "i" : "imperfect",
        "f" : "future",
        "a" : "aorist",
        "x" : "perfect",
        "y" : "pluperfect"
        }, 'tense')
    return t.get(code)

def voice(code):
    v = Code({
        "a" : "active",
        "m" : "middle",
        "p" : "passive"
        }, 'voice')
    return v.get(code)

def mood(code):
    m = Code({
        "i" : "indicative",
        "s" : "subjunctive",
        "o" : "optative",
        "d" : "imperative",
        "n" : "infinitive",
        "p" : "participle"
        }, 'mood')
    return m.get(code)

def case(code):
    c = Code({
        "n" : "nominative",
        "v" : "vocative",
        "g" : "genitive",
        "d" : "dative",
        "a" : "accusative"
        }, 'case')
    return c.get(code)

def number(code):
    n = Code({
        's': 'singular',
        'p': 'plural'
        }, 'numbers')
    return n.get(code)

def gender(code):
    g = Code({
        'f': 'feminine',
        'm': 'masculine',
        'n': 'neuter'
        }, 'gender')
    return g.get(code)

def degree(code):
    d = Code({
        'c': 'comparative',
        's': 'superlative'
        }, 'degree')
    return d.get(code)

def part_of_speech(code):
    wordtype = Code({
        'a-': 'adjective',
        'c-': 'conjunction',
        'd-': 'adverb',
        'n-': 'noun',
        'p-': 'preposition',
        'ra': 'article',
        'rd': 'demonstrative',
        'ri': 'interrogative',
        'rp': 'personal pronoun',
        'rr': 'relative pronoun',
        'v-': 'verb',
        'x-': 'exclamation',
        'i-': 'interjection'
        }, 'word-type')
    return wordtype.get(code)
