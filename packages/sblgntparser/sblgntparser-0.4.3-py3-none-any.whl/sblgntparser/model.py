# -*- coding: utf-8 -*-

import logging
log = logging.getLogger(__name__)

class Text():
    def __init__(self, sentences, author, bookindex):
        self._sentences = sentences
        self._bookindex = bookindex

    def bookindex(self):
        '''
        Returns the index of the book.
        The bookname can be returned using `tools.bookname(index)`
        '''
        return self._bookindex

    def sentences(self):
        '''
        Returns an generator of all the sentences contained in the text.
        '''
        for sentence in self._sentences:
            yield sentence

    def __len__(self):
        return len(self._sentences)

    def find(self, sought, view='lemma'):
        '''
        Returns a word instance for the hit if the "sought" word is found in the text.
        Per default the "lemma" view of the words is compared.
        You can specify the desired view with the optional "view" option.
        '''
        hits = []
        for sentence in self._sentences:
            hits += sentence.find(sought, view)
        return hits

    def words(self):
        '''
        Returns an generator of all the words contained in this text.
        '''
        for sentence in self._sentences:
            for word in sentence.words():
                yield word

    def __str__(self):
        return ' '.join([ word.views['text'] for word in self.words() ])

class Sentence():
    def __init__(self, wordlist):
        if wordlist:
            self.wordlist = wordlist
        else:
            self.wordlist = []

    def append(self, word):
        '''
        Appends the word to the sentence.
        '''
        self.wordlist.append(word)

    def find(self, sought, view='lemma'):
        '''
        Returns a word instance for the hit if the "sought" word is found in the sentence.
        Per default the "lemma" view of the words is compared.
        You can specify the desired view with the optional "view" option.
        '''
        for word in self.wordlist:
            if sought == word.views[view]:
                yield word

    def words(self):
        '''
        Returns a list of all the words in the sentence.
        '''
        return self.wordlist

    def word(self, position):
        '''
        Returns the word instance at the given position in the sentence, None if not found.
        '''
        if 0 <= position < len(self.wordlist):
            return self.wordlist[position]
        else:
            log.warn('position "{}" is not in sentence of length "{}"!'.format(position, len(self.wordlist)))
            raise IndexError()

    def __len__(self):
        return len(self.wordlist)

    def __str__(self):
        return ' '.join([ str(word) for word in self.wordlist ])

class Word():
    def __init__(self, word, sentence, position):
        self.textpos = word['text_position']
        self.book = word['book']
        self.chapter = word['chapter']
        self.verse = word['verse']
        self.part_of_speech = word['part_of_speech']
        self.codes = word['codes']
        self.views = word['views']
        self._sentence = sentence
        self._position = position

    def __str__(self):
        '''
        Returns the "text" view of this word.
        Shorthand for word.views['text']
        '''
        return self.views['text']

    def sentence(self):
        '''
        Returns the sentence that contains the instance of this word.
        '''
        return self._sentence

    def subsentence(self):
        '''
        Returns the subsentence that contains this word, otherwise the whole sentence.
        TODO
        '''
        subsentence = []
        for word in self.sentence()[:self._position:-1]:
            # left search
            pass
        for word in self.sentence()[:self._position]:
            # right search
            pass

    def position(self):
        '''
        Returns the position in the sentence.
        '''
        return self._position

    def neighbors(self):
        '''
        Returns the left and right neighbors as Word instance.
        If the word is the first one in the sentence only the right neighbor is returned and vice versa.
        '''
        if len(self._sentence) == 1:
            return {
                'left': None,
                'right': None
            }
        else:
            p = self._position
            if -1 < p < len(self._sentence):
                if 0 == self._position:
                    return {
                        'left': None,
                        'right': self._sentence.word(p+1)
                    }
                elif 0 < self._position < len(self._sentence) - 1:
                    return {
                        'left':  self._sentence.word(p-1),
                        'right': self._sentence.word(p+1)
                    }
                else:
                    return {
                        'left': self._sentence.word(p-1),
                        'right': None
                    }
            else:
                raise IndexError()