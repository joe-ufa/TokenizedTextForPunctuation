# -*- coding: utf-8 -*-
"""
@author: jmarks
Code to tokenize raw text.
"""

# Python libraries.
import re            # Regular-expression classes: see https://docs.python.org/2/library/string.html and https://docs.python.org/2/library/re.html .

# ------------------------- Class TokenizedText -------------------------------
# The TokenizedText class is used to tokenize raw text from a document
# and to organize into paragraphs and sentences.
class TokenizedText:   
    # Constants used to tokenize text.
    PARA_DELIMITER = "\n\n"
    CAPS = "([A-Z])"
    PREFIXES = "(Mr|St|Mrs|Ms|Dr)[.]"
    SUFFIXES = "(Inc|Ltd|Jr|Sr|Co)"
    STARTERS = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    ACRONYMS = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    WEBSITES = "[.](com|net|org|io|gov)"
    DIGITS = "([0-9])"
    

    # Class TokenizedText
    # Object initialization.
    def __init__(self):
        self.whole_doc = ''                     # Text from the file as read from disk.
        self.paragraphs = []                    # List of paragraphs.
        self.paragraph_sentences = []           # List of sentences in each paragraph.

    # Class TokenizedText
    # Takes a sentence as input and returns a list of sentences after ionserting inferred periods.
    # def split_sentences_with_inferred_periods(self, )

      
    # Class TokenizedText
    # Sentence-splitting code courtesy of Stackoverflow, with some refinements.
    # Replaces newlines and carriage returns with spaces.
    # Differentiates between periods that terminate sentences (substituted temporarily
    # as <prd>) and those that don't (substituted temporarily as <stop>). Also
    # catches other sentence terminators, such as '!' and '?'. Also handles
    # issues with quotes and slashes. Finaly, is careful not to alter the
    # character count, which would mess up the sentence and paragraph offset counts.
    # See https://docs.python.org/2/library/string.html for documentation on string methods.
    # See https://docs.python.org/2/library/re.html for documentation on regular expressions.
    def split_into_sentences(self, text):
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
        text = text.replace(",", ",<stop>")
        text = text.replace("<prd>",".")
        text = text + "<stop>"
        sentences = text.split("<stop>")
        sentences = sentences[:-1]
        sentences = [s for s in sentences if s != '']
        return sentences


    # Class TokenizedText
    # Populates the TokenizedText object for the document in the file filename.
    def populate_obj(self, text):
        text = text.replace("\\n"," \n")         # Substitute newline characters for raw '\n', using spaces to maintain offset counts.
        text = text.replace(r"\\.br\\", "      \n")   # Substitute newline characters for these strings, using spaces to maintain offset counts.
        self.whole_doc = text
        self.paragraphs = [(para + self.PARA_DELIMITER) for para in text.split(self.PARA_DELIMITER)]
        self.paragraph_sentences = [self.split_into_sentences(para) for para in self.paragraphs]
        #paragraph_sentences_tmp = [re.sub("\d+(\.\d*)?", "<NUM>", s) for s_list in self.paragraph_sentences for s in s_list]
        #self.paragraph_word_lists = [[word for word in s.split()] for s in paragraph_sentences_tmp]    # Built-in string method for splitting strings into words.
 
# ------------------------- Class TokenizedText -------------------------------
