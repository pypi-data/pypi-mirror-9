# -*- coding: utf-8 -*-

import os.path
import re
import logging
log = logging.getLogger(__name__)

from sblgntparser import codes as sblgntcodes
from sblgntparser import model, tools

'''
    A python module that parses texts in the format the SBLGNT uses

    http://morphgnt.org/sblgnt/

    todo:
        - refactor classes to seperate module, like model.py
'''

punctuation = {
    'sentence': [ '.', ';' ],   # period, question mark
    'subsentence': [ ',', u'·' ] # comma, semicolon
}
# period, comma, question mark, semicolon

def parse(filepath):
    if os.path.exists(filepath):
        raw_text = ''
        try:
            with open(filepath) as f:
                raw_text = f.readlines()
        except IOError as e:
            log.exception(e)
        else:
            if raw_text:
                bookindex = None
                sentences = []
                sentence = model.Sentence([])
                for index, line in enumerate(raw_text):
                    word = parse_line(index, line, sentence, len(sentence))
                    if not bookindex:
                        bookindex = word.book
                    sentence.append(word)
                    for marker in punctuation['sentence']:
                        if marker in word.views['text']:
                            sentences.append(sentence)
                            sentence = model.Sentence([])
                return model.Text(sentences, tools.bookname(bookindex), bookindex)
            else:
                log.error('"{}" is empty!'.format(filepath))
    else:
        log.warn('Could not find file "{}"!'.format(filepath))

def parse_line(index, line, sentence, position):
    parts = line.split()
    if len(parts) is not 7:
        log.warn('Malformed line: "{}"'.format(line))
    else:
        book, chapter, verse = parse_index(parts[0])
        pos = parse_part_of_speech(parts[1])
        codes = parse_parsing_code(parts[2])
        text, word, normalised, lemma = tuple(parts[3:])
        return model.Word({
            'text_position': index,
            'book': int(book),
            'chapter': int(chapter),
            'verse': int(verse),
            'part_of_speech': pos,
            'codes': codes,
            'views': {
                'text': text,
                'word': word,
                'norm': normalised,
                'lemma': lemma
                }
            },
            sentence, position)

def parse_index(part):
    matcher = re.compile(r'(\d{2})(\d{2})(\d{2})')
    res = matcher.match(part)
    return res.groups()

def parse_part_of_speech(part):
    return sblgntcodes.part_of_speech(part)

def parse_parsing_code(part):
    if len(part) is not 8:
        log.warn('bad parsing code: "{}"!'.format(part))
    else:
        # see https://github.com/morphgnt/tischendorf/blob/master/code/rptag.py
        # person, tense, voice, mood, case, number, gender, degree
        codes = [ _ for _ in part ]
        person = sblgntcodes.person(codes[0])
        tense = sblgntcodes.tense(codes[1])
        voice = sblgntcodes.voice(codes[2])
        mood = sblgntcodes.mood(codes[3])
        case = sblgntcodes.case(codes[4])
        number = sblgntcodes.number(codes[5])
        gender = sblgntcodes.gender(codes[6])
        degree = sblgntcodes.degree(codes[7])
        return {
            'person': person,
            'tense': tense,
            'voice': voice,
            'mood': mood,
            'case': case,
            'number': number,
            'gender': gender,
            'degree': degree
        }

