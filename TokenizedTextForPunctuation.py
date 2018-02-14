# -*- coding: utf-8 -*-
"""
@author: jmarks
Code to tokenize raw text.
"""

# Python libraries.
import re            # Regular-expression classes: see https://docs.python.org/2/library/string.html and https://docs.python.org/2/library/re.html .
import csv           # CSV file I/O.

# ------------------------- Class TokenizedText -------------------------------
# The TokenizedText class is used to tokenize raw text from a document
# and to organize into paragraphs and sentences.
class TokenizedText:   
    # Constants used to tokenize text.
    CSV_SEPARATOR = " "
    WHITE_SPACE = (' ', '\t', '\n')
    PUNCTUATION_REGEX = "[\.\!\?\;\:\,]$"
    PARA_DELIMITER = "\n\n"
    NUM_REGEX = "\d+(\.\d*)?"
    CAPS = "([A-Z])"
    PREFIXES = "(Mr|St|Mrs|Ms|Dr)[.]"
    SUFFIXES = "(Inc|Ltd|Jr|Sr|Co)"
    STARTERS = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    ACRONYMS = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    WEBSITES = "[.](com|net|org|io|gov)"
    DIGITS = "([0-9])"
    SENTENCE_END_BIGRAMS_FILE = "sentence_end_bigrams.csv"
    SENTENCE_BEGIN_BIGRAMS_FILE = "sentence_begin_bigrams.csv"
    BEGIN_BIGRAMS = []
    END_BIGRAMS = []
    

    # Class TokenizedText
    # Object initialization.
    def __init__(self):
        self.whole_doc = ''                     # Text from the file as read from disk.
        self.paragraphs = []                    # List of paragraphs.
        self.paragraph_sentences = []           # List of sentences in each paragraph.
        self.paragraph_sentences_with_inferred_punctuation = []     # List of sentences in each paragraph with inferred punctuation added.
        self.sentence_end_bigrams = []
        self.sentence_begin_bigrams = []


    # Class TokenizedText
    # Sentence-splitting code courtesy of Stackoverflow, with some refinements.
    # Replaces newlines and carriage returns with spaces.
    # Differentiates between periods that terminate sentences (substituted temporarily
    # as <prd>) and those that don't (substituted temporarily as <stop>). Also
    # catches other sentence terminators, such as ';', ',' (optionally), '!' and '?'. Also handles
    # issues with quotes and slashes. Finaly, is careful not to alter the
    # character count, which would mess up the sentence and paragraph offset counts.
    # See https://docs.python.org/2/library/string.html for documentation on string methods.
    # See https://docs.python.org/2/library/re.html for documentation on regular expressions.
    def split_into_sentences(self, text, treat_comma_as_period):
        text = text.replace("\n"," ")
        text = text.replace("\r"," ")
        text = text.replace("%0D", "   ")
        text = text.replace("%0d", "   ")
        text = text.replace("%0A", "   ")
        text = text.replace("%0a", "   ")
        text = re.sub(self.PREFIXES,"\\1<prd>",text)
        text = re.sub(self.WEBSITES,"<prd>\\1",text)
        if "Ph.D" in text:
            text = text.replace("Ph.D.","Ph<prd>D<prd>")
        text = re.sub("\s" + self.CAPS + "[.] "," \\1<prd> ",text)
        text = re.sub(self.ACRONYMS+" "+self.STARTERS,"\\1<stop> \\2",text)
        text = re.sub(self.CAPS + "[.]" + self.CAPS + "[.]" + self.CAPS + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
        text = re.sub(self.CAPS + "[.]" + self.CAPS + "[.]","\\1<prd>\\2<prd>",text)
        text = re.sub(" "+self.SUFFIXES+"[.] "+self.STARTERS," \\1<stop> \\2",text)
        text = re.sub(" "+self.SUFFIXES+"[.]"," \\1<prd>",text)
        text = re.sub(" " + self.CAPS + "[.]"," \\1<prd>",text)
        text = re.sub(self.DIGITS + "[.]" + self.DIGITS,"\\1<prd>\\2",text)
        if "”" in text:
            text = text.replace(".”","”.")
        if "\"" in text:
            text = text.replace(".\"","\".")
        if "!" in text:
            text = text.replace("!\"","\"!")
        if "?" in text:
            text = text.replace("?\"","\"?")
        if "e.g." in text:
            text = text.replace("e.g.","e<prd>g<prd>")
        if "i.e." in text:
            text = text.replace("i.e.","i<prd>e<prd>")
        text = text.replace(";",";<stop>")
        text = text.replace(".",".<stop>")
        text = text.replace("?","?<stop>")
        text = text.replace("!","!<stop>")
        if treat_comma_as_period:
            text = text.replace(",", ",<stop>")
        text = text.replace("<prd>",".")
        text = text + "<stop>"
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s for s in sentences if s != '']
        return sentences
    
    
    # Class TokenizedText
    # Takes raw text and inserts '<stop>' where an inferred period should be.
    def insert_stops(self, text):
        i = 0
        while i < len(text):
            if ((text[i] in self.WHITE_SPACE)):
                prefix_word_list = [re.sub(self.NUM_REGEX, "<NUM>", word) for word in text[:i].split()]
                if (len(prefix_word_list) >= 2) and ((re.sub(self.PUNCTUATION_REGEX, "", prefix_word_list[0]), re.sub(self.PUNCTUATION_REGEX, "", prefix_word_list[1])) in self.sentence_begin_bigrams):
                    return '<stop>' + text[:i+1] + self.insert_stops(text[i+1:])
                if (len(prefix_word_list) >= 2) and ((re.sub(self.PUNCTUATION_REGEX, "", prefix_word_list[-2]), re.sub(self.PUNCTUATION_REGEX, "", prefix_word_list[-1])) in self.sentence_end_bigrams):
                    return text[:i] + '<stop>' + self.insert_stops(text[i:])
            i = i + 1
        return text             # Recursion base case.


    # Class TokenizedText
    # Takes a sentence as input and returns a list of sentences after inserting inferred periods.
    def split_into_sentences_with_inferred_punctuation(self, text):
        return self.split_into_sentences(self.insert_stops(text), False)
    

    # Class TokenizedText
    # Populates the TokenizedText object for the document in the file filename.
    def populate_obj(self, text, treat_comma_as_period):
        text = text.replace("\\n"," \n")         # Substitute newline characters for raw '\n', using spaces to maintain offset counts.
        text = text.replace(r"\\.br\\", "      \n")   # Substitute newline characters for these strings, using spaces to maintain offset counts.
        self.whole_doc = text
        self.paragraphs = [(para + self.PARA_DELIMITER) for para in text.split(self.PARA_DELIMITER)]
        self.paragraph_sentences = [self.split_into_sentences(para, treat_comma_as_period) for para in self.paragraphs]
        self.paragraph_sentences_with_inferred_punctuation = [self.split_into_sentences_with_inferred_punctuation(para) for para in self.paragraphs]
        with open(self.SENTENCE_BEGIN_BIGRAMS_FILE, 'rb') as csvfile:
            bigram_reader = csv.reader(csvfile, delimiter = self.CSV_SEPARATOR)
            for row in bigram_reader:
                self.sentence_begin_bigrams.append((row[0], row[1]))
        with open(self.SENTENCE_END_BIGRAMS_FILE, 'rb') as csvfile:
            bigram_reader = csv.reader(csvfile, delimiter = self.CSV_SEPARATOR)
            for row in bigram_reader:
                self.sentence_end_bigrams.append((row[0], row[1]))


 
# ------------------------- Class TokenizedText -------------------------------

# Test loop.
#s = " The quick  red  fox  jumped over the lazy brown dog, maybe.  Maybe not!"
s = "She is an older male with prostate cancer and who knows what else."
tt = TokenizedText()
tt.populate_obj(s, False)
print tt.insert_stops(s)