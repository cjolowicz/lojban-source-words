#!/usr/bin/python

from gismuloaders import *

import sys
import os.path
import sqlite3

##
# Load from all files into all tables.
#
def main(directory, filename):
    connection = sqlite3.connect(filename)
    loaders = [
        (CmavoLoader, 'cmavo.txt'),
        (GismuLoader, 'gismu.txt'),
        (ObliqueKeywordsLoader, 'oblique_keywords.txt'),
        (ArabicLoader, 'lojban-source-words_ar.txt'),
        (ChineseLoader, 'lojban-source-words_zh.txt'),
        (EnglishLoader, 'lojban-source-words_en.txt'),
        (HindiLoader, 'lojban-source-words_hi.txt'),
        (RussianLoader, 'lojban-source-words_ru.txt'),
        (SpanishLoader, 'lojban-source-words_es.txt')]

    for loaderclass, filename in loaders:
        print 'Loading %s ...' % filename

        loader = loaderclass(connection,
                             os.path.join(directory, filename))

        loader.open()
        loader.load()
        loader.close()

##
# Main entry point.
#
if __name__ == '__main__':
    directory = os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.realpath(sys.argv[0]))),
        'data')

    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    else:
        filename = 'dictionary.sql'

    main(directory, filename)
