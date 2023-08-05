#*****************************
# Python-ucto
#   by Maarten van Gompel
#   Centre for Language Studies
#   Radboud University Nijmegen
#
#   Licensed under GPLv3
#****************************/

from libcpp.string cimport string
from libcpp.vector cimport vector
from libcpp cimport bool
from libc.stdint cimport *



cdef extern from "ucto/tokenize.h" namespace "Tokenizer":
    cdef cppclass Token:
        string texttostring()
        string typetostring()
        int role

    cdef cppclass TokenizerClass:
        bool init(string & settingsfile)

        bool setLowercase(bool)
        bool setUppercase(bool)
        bool setSentenceDetection(bool)
        bool setParagraphDetection(bool)
        bool setQuoteDetection(bool)
        bool setSentencePerLineOutput(bool)
        bool setSentencePerLineInput(bool)
        bool setXMLOutput(bool, string & docid)
        bool setXMLInput(bool)
        int setDebug(int)

        void tokenize(string,string) nogil
        int tokenizeLine(string &) nogil
        vector[string] getSentences() nogil
        vector[Token] getSentence(int) nogil
        int countSentences(bool forcebuffer) nogil
        int flushSentences(int count) nogil
