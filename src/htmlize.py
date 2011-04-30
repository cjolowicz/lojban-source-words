#!/usr/bin/python2.5

from version import VERSION
from gismu import GismuFactory
from format import Formatter
from util import *

import sys
import codecs
import sqlite3
import re
from datetime import datetime
from collections import defaultdict
from itertools import izip, count, dropwhile

##
# Quote ampersand and angular brackets.
#
def htmlquote(s):
    if s:
        s = s.replace('&', '&amp;')
        s = s.replace('<', '&lt;')
        s = s.replace('>', '&gt;')
    return s

q = htmlquote

##
# Exception indicating that no gismu or lujvo was matched.
#
class MatchFailed(Exception):
    pass

##
# Markup gismu and lujvo in a text.
#
class LujvoMarkup(object):
    falsePositives = dict.fromkeys('''\
fenced
frozen
sudden
tragic
bitten
banker
protected
container
runner
voiced
millet
filled
gender
voices
trades
manner
prefer
preferred
number
causal
person
serves
perceives
mitten
mental
places
postum
practices
called
cackle
simple
cursed'''.splitlines())

    format = '''\
<a class="gismuref" href="%(file)s#%(gismu)s" title="%(title)s">%(word)s</a>'''

    def __init__(self, gismudict, rafsidict, outfilename):
        self._gismudict = gismudict
        self._rafsidict = rafsidict
        self._outfilename = outfilename

    def markup(self, text):
        _words, words = text.split(), []

        for word, i in izip(_words, count()):
            before = after = ''

            def dropnotalpha(word):
                return ''.join(dropwhile(
                        lambda c: c not in 'abcdefghijklmnopqrstuvwxyz',
                        word))

            def rdropnotalpha(word):
                return ''.join(reversed(
                        dropnotalpha(reversed(word))))

            word, before = dropnotalpha(word), word
            if word:
                before = before[:-len(word)]

            word, after = rdropnotalpha(word), word
            if word:
                after = after[len(word):]

            if not (i+1 < len(_words) and
                    word == 'cmavo' and
                    _words[i+1] == 'list'):
                word = self.markupWord(word)

            if "tadjyju'o" in text:
                print 'word: "%s" "%s" "%s"]' % (before,word,after)

            words.append(word.join((before, after)))

        return ' '.join(words)

    def markupWord(self, word):
        def debug(s):
            if word == "tadjyju'o":
                print s

        if len(word) >= 5 and word not in self.falsePositives:
            try:
                return self._markupWord(word, '', debug)
            except MatchFailed:
                pass

        return word

    def _markupWord(self, word, result, debug):
        if len(word) < 3:
            debug(":-( len(%s)<3" % word)
            raise MatchFailed, word

        if len(word) == 5 and word in self._gismudict:
            debug(":-) %s is gismu" % word)
            result += self.link(word, word)
            return result

        if len(word) >= 8 and word[4] == 'y':
            prefix = word[:4]
            suffix = word[5:]
            for vowel in 'aeiou':
                if prefix + vowel in self._gismudict:
                    result += self.link(prefix, prefix + vowel)
                    result += 'y'
                    return self._markupWord(suffix, result, debug)
            debug(":-( %s is no long lujvo")
            raise MatchFailed, word

        prefix, suffix = (word[0:3], word[3:]) \
            if word[2] != "'" else (word[0:4], word[4:])

        if prefix not in self._rafsidict:
            debug(":-( %s is not rafsi" % word)
            raise MatchFailed, prefix

        result += self.link(prefix, self._rafsidict[prefix])

        if not suffix:
            debug(":-) %s has no suffix" % word)
            return result

        if suffix[0] == 'y':
            result += 'y'
            suffix = suffix[1:]

        return self._markupWord(suffix, result, debug)

    def link(self, word, gismu):
        keyword = iter(self._gismudict[gismu].keywords[1]).next()
        return self.format % dict(file=self._outfilename % gismu[0],
                                  gismu=gismu,
                                  title=q(keyword),
                                  word=word)

##
# Print a sourceword entry.
#
class SourcewordFormatter(Formatter):
    format = '''\
<span class="sourcewordentry">
  <span class="sourcewordnumber">%(sourcewordnumber)</span>
  <span class="sourceword transcription">*%(transcription)</span>
  <span class="sourceword" xml:lang="%(langcode)" lang="%(langcode)" dir="%(direction)">%(sourceword)</span>
  <span class="sourceword simplified" xml:lang="%(langcode)" lang="%(langcode)" dir="%(direction)">(%(alternative))</span>
  <span class="transliteration">[%(transliteration)]</span>
  <span class="translation">%(translation)</span>
  <span class="comment">(?)</span>
</span>'''

    def __init__(self, sourceword, sourcewordnumber):
        super(SourcewordFormatter, self).__init__()

        self.sourcewordnumber = sourcewordnumber
        self.sourceword = q(sourceword.sourceword)
        self.alternative = q(sourceword.alternative)
        self.transcription = q(sourceword.transcription)
        self.transliteration = q(sourceword.transliteration)
        self.translation = q(sourceword.translation)
        self.langcode = sourceword.langcode
        self.direction = 'rtl' if self.langcode == 'ar' else 'ltr'

        lines = self.format.splitlines()

        if not self.sourcewordnumber:
            lines = removelike(lines, '"sourcewordnumber"')

        if not self.sourceword:
            lines = removelike(lines, '"sourceword"')
            lines = removelike(lines, '"comment"')
        else:
            lines = removelike(lines, '"sourceword transcription"')

        if not self.alternative:
            lines = removelike(lines, '"sourceword simplified"')

        if not self.transliteration:
            lines = removelike(lines, '"transliteration"')

        if not self.translation or self.sourceword == self.translation:
            lines = removelike(lines, '"translation"')

        if not (sourceword.comment and ('dubious' in sourceword.comment or
                                        'FIXIT' in sourceword.comment)):
            lines = removelike(lines, '"comment"')

        self.format = '\n'.join(lines)

##
# Print a gismu etymology.
#
class EtymologyFormatter(Formatter):
    format = '''\
<span class="langetymology">
  <span class="lang">%(language)</span>
  <span class="sourcewordentries">
    %(sourcewordentries)
  </span>
</span>'''

    def __init__(self, language, sourcewords):
        super(EtymologyFormatter, self).__init__()
        self.language = language
        self._sourcewords = sourcewords

    def sourcewordentries(self, file):
        sourcewordnumber = 1 if len(self._sourcewords) > 1 else 0

        for sourceword in self._sourcewords:
            SourcewordFormatter(sourceword, sourcewordnumber)(file)
            if sourcewordnumber:
                sourcewordnumber += 1

##
# Print a gismu entry.
#
class GismuFormatter(Formatter):
    format = '''\
<div class="entry">
  <span class="gismu" id="%(gismu)">%(gismu)</span>
  <span class="rafsilist">%(rafsilist)</span>
  <span class="gismudef">&ldquo;%(definition)&rdquo;</span>
  <span class="keywords">%(keywords)</span>
  <span class="etymology">%(etymology)</span>
  <span class="references">%(references)</span>
  <span class="remark">%(remark)</span>
</div>'''

    def __init__(self, gismu, context):
        super(GismuFormatter, self).__init__()
        self._gismu = gismu
        self._context = context

        self.setSourcewords()
        self.setFormat()

    def setFormat(self):
        lines = self.format.splitlines()

        if not self._gismu.rafsi:
            lines = removelike(lines, '"rafsilist"')

        if not self._sourcewords:
            lines = removelike(lines, '"etymology"')

        if not self._gismu.xrefs:
            lines = removelike(lines, '"references"')

        if not self._gismu.comment:
            lines = removelike(lines, '"remark"')

        self.format = '\n'.join(lines)

    def setSourcewords(self):
        sourcewords = defaultdict(list)
        for sourceword in self._gismu.sourcewords:
            if sourceword.score:
                sourcewords[sourceword.language].append(sourceword)

        self._sourcewords = defaultdict(list)
        for language in sourcewords:
            sourcewords[language].sort(key=lambda x: x.score,
                                       reverse=True)

            done = set()
            for sourceword in sourcewords[language]:
                if sourceword.sourceword not in done:
                    self._sourcewords[language].append(sourceword)
                done.add(sourceword.sourceword)

    def gismu(self, file):
        file.write(self._gismu.gismu)

    def rafsilist(self, file):
        for rafsi in self._gismu.rafsi:
            file.write('''\
<span class="rafsi" id="%(rafsi)s">[%(rafsi)s]</span>''' % dict(rafsi=rafsi))

    def definition(self, file):
        file.write(self._context.markup(q(self._gismu.definition)))

    def keywords(self, file):
        for i, keywords in sorted(self._gismu.keywords.iteritems()):
            keywords = q('; '.join(keywords))
            keywords = self._context.markup(keywords)
            file.write('''\
<span class="keywordentry">
  <span class="place">x%(place)s</span>
  <span class="keyword">%(keywords)s</span>
</span>''' % dict(place=i, keywords=keywords))

    def etymology(self, file):
        languages = ['Arabic', 'Chinese', 'English',
                     'Hindi', 'Russian', 'Spanish']

        for language in languages:
            if self._sourcewords[language]:
                EtymologyFormatter(language,
                                   self._sourcewords[language])(file)

    def remark(self, file):
        file.write(self._context.markup(q(self._gismu.comment)))

    def references(self, file):
        references = q(self._gismu.xrefs)
        references = re.sub(r'^cf\.?\s*', u'\u2192 ', references)
        references = self._context.markup(references)
        file.write(references)

##
# Print the HTML head.
#
class HeadFormatter(Formatter):
    def __init__(self, first, previous, next, last):
        self.first = first
        self.previous = previous
        self.next = next
        self.last = last

    author = 'mublin'
    description = 'Source words for Lojban gismu'
    keywords = 'etymology, Lojban, gismu'
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    copyright = 'README.html'
    made = 'mailto:mublin@dealloc.org'
    style = 'style.css'
    inline_style = ''
    title = 'Etymology of Lojban'
    format = '''\
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <meta name="author" content="%(author)" />
  <meta name="description" content="%(description)" />
  <meta name="keywords" content="%(keywords)" />
  <meta name="date" content="%(date)" />
  <link rel="copyright" href="%(copyright)" title="Public domain" />
  <link rev="made" href="%(made)" title="Feedback" />
  <link rel="stylesheet" type="text/css" href="%(style)" />
  <link rel="first" href="%(first)" />
  <link rel="previous" href="%(previous)" />
  <link rel="next" href="%(next)" />
  <link rel="last" href="%(last)" />
  <style type="text/css">
/*<![CDATA[*/
%(inline_style)
/*]]>*/
  </style>

  <title>%(title)</title>
</head>'''

##
# Print the HTML body.
#
class BodyFormatter(Formatter):
    version = VERSION
    date = datetime.now().strftime('%B %Y')
    title = 'Etymology of Lojban'
    format = '''\
<body>
  <div class="content">
  <h1>%(title)<br/><span id="version">Version %(version), %(date)</span></h1>
    <div class="index">
      %(index)
    </div>
    <div class="main">
      <h3 class="initial" id="initial">%(initial)</h3>

      %(main)
    </div>
  </div>
</body>'''

    def __init__(self, initial, gismudict, rafsidict, outfilename):
        super(BodyFormatter, self).__init__()
        self.initial = initial
        self._gismudict = gismudict
        self._rafsidict = rafsidict
        self._outfilename = outfilename

    def index(self, file):
        for initial in 'bcdfgjklmnprstvxz':
            if initial == self.initial:
                format = '<a href="%(file)s" accesskey="%(initial)s" class="current">%(initial)s</a>'
            else:
                format = '<a href="%(file)s" accesskey="%(initial)s">%(initial)s</a>'
            file.write(format % dict(initial=initial,
                                     file=outfilename % initial))
            if initial != 'z':
                file.write('\n')
                file.write('      ')

    def main(self, file):
        for gismu in sorted(self._gismudict):
            if gismu[0] == self.initial:
                GismuFormatter(self._gismudict[gismu], self)(file)

    def markup(self, text):
        text = self.markupExponent(text)
        text = self.markupSumti(text)
        text = self.markupGismu(text)
        return text

    def markupExponent(self, text):
        text = re.sub(r'([0-9]+)E([-0-9]+)', r'\1E<sup>\2</sup>', text)
        text = re.sub(r'([0-9]+)\*\*([-0-9]+)', r'\1<sup>\2</sup>', text)
        return text

    def markupSumti(self, text):
        return re.sub(r'\b(x[0-9])\b', r'<span class="sumti">\1</span>', text)

    def markupGismu(self, text):
        return LujvoMarkup(self._gismudict,
                           self._rafsidict,
                           self._outfilename).markup(text)

##
# Print the HTML document.
#
class DocumentFormatter(Formatter):
    format = '''\
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html 
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
%(head)

%(body)
</html>
'''
    def __init__(self, gismudict, rafsidict, initial,
                 first, previous, next, last,
                 outfilename):
        super(DocumentFormatter, self).__init__()
        self.head = HeadFormatter(outfilename % first,
                                  outfilename % previous,
                                  outfilename % next,
                                  outfilename % last)
        self.body = BodyFormatter(initial,
                                  gismudict,
                                  rafsidict,
                                  outfilename)

##
# Generate HTML.
#
def main(infilename, outfilename):
    sys.stderr.write('Loading data...')

    connection = sqlite3.connect(infilename)
    factory = GismuFactory(connection)
    gismudict = dict((gismu, factory.create(gismu))
                     for gismu in factory.gismu())
    rafsidict = dict((rafsi, gismu)
                     for gismu, entry in gismudict.iteritems()
                     for rafsi in entry.rafsi)

    sys.stderr.write(' done.\n')
    sys.stderr.write('Generating HTML... ')

    initials = 'bcdfgjklmnprstvxz'

    for initial, i in zip(initials, count()):
        sys.stderr.write(initial)

        outfile = codecs.getwriter('utf8')(
            open(outfilename % initial, 'w'))

        formatter = DocumentFormatter(
            gismudict,
            rafsidict,
            initial,
            initials[0],
            initials[i-1 if i else 0],
            initials[i+1 if i+1 < len(initials) else -1],
            initials[-1],
            outfilename)

        formatter(outfile)

    sys.stderr.write(".\n")

##
# Main entry point.
#
if __name__ == '__main__':
    if len(sys.argv) >= 3:
        infilename, outfilename = sys.argv[1], sys.argv[2]
    elif len(sys.argv) == 2:
        infilename, outfilename = sys.argv[1], '%s.html'
    else:
        infilename, outfilename = 'dictionary.sql', '%s.html'

    main(infilename, outfilename)
