from gismutables import *
from collections import defaultdict

##
# Description of a gismu.
#
class Gismu(object):
    def __init__(self, gismu, definition, comment, xrefs, rafsi, keywords):
        self.gismu = gismu
        self.definition = definition
        self.comment = comment
        self.xrefs = xrefs
        self.rafsi = rafsi
        self.keywords = keywords
        self.sourcewords = []

    def addSourceword(self, sourceword):
        self.sourcewords.append(sourceword)

##
# Description of a source word.
#
class Sourceword(object):
    def __init__(self, row):
        self.langcode = row['langcode']
        self.language = row['language']
        self.sourceword = row.get('sourceword')
        self.transliteration = row.get('transliteration')
        self.translation = row.get('translation')
        self.klass = row.get('klass')
        self.transcription = row.get('transcription')
        self.score = int(row.get('score'))
        self.comment = row.get('comment')
        self.alternative = row.get('alternative')

##
# Description of a Chinese source word.
#
class ChineseSourceword(Sourceword):
    def __init__(self, row):
        row['klass'] = None
        row.setdefault('langcode', 'zh')
        row.setdefault('language', 'Chinese')
        super(ChineseSourceword, self).__init__(row)

##
# Description of a Hindi source word.
#
class HindiSourceword(Sourceword):
    def __init__(self, row):
        row['alternative'] = None
        row.setdefault('langcode', 'hi')
        row.setdefault('language', 'Hindi')
        super(HindiSourceword, self).__init__(row)

##
# Description of an Arabic source word.
#
class ArabicSourceword(HindiSourceword):
    def __init__(self, row):
        row['klass'] = None
        row.setdefault('langcode', 'ar')
        row.setdefault('language', 'Arabic')
        super(ArabicSourceword, self).__init__(row)

##
# Description of a Russian source word.
#
class RussianSourceword(ArabicSourceword):
    def __init__(self, row):
        row['klass'] = None
        row.setdefault('langcode', 'ru')
        row.setdefault('language', 'Russian')
        super(ArabicSourceword, self).__init__(row)

##
# Description of a Spanish source word.
#
class SpanishSourceword(RussianSourceword):
    def __init__(self, row):
        row['transliteration'] = None
        row.setdefault('langcode', 'es')
        row.setdefault('language', 'Spanish')
        super(SpanishSourceword, self).__init__(row)

##
# Description of an English source word.
#
class EnglishSourceword(SpanishSourceword):
    def __init__(self, row):
        row['translation'] = row['sourceword']
        row.setdefault('langcode', 'en')
        row.setdefault('language', 'English')
        super(EnglishSourceword, self).__init__(row)

##
# Factory of gismu descriptions.
#
class GismuFactory(object):
    def __init__(self, connection):
        self.definitions = DefinitionTable(connection)
        self.rafsi = RafsiTable(connection)
        self.keywords = KeywordTable(connection)
        self.chinese = ChineseTable(connection)
        self.arabic = ArabicTable(connection)
        self.english = EnglishTable(connection)
        self.hindi = HindiTable(connection)
        self.spanish = SpanishTable(connection)
        self.russian = RussianTable(connection)

    def _openTables(self):
        self.definitions.open()
        self.rafsi.open()
        self.keywords.open()
        self.chinese.open()
        self.arabic.open()
        self.english.open()
        self.hindi.open()
        self.spanish.open()
        self.russian.open()

    def _closeTables(self):
        self.definitions.close()
        self.rafsi.close()
        self.keywords.close()
        self.chinese.close()
        self.arabic.close()
        self.english.close()
        self.hindi.close()
        self.spanish.close()
        self.russian.close()

    def gismu(self, **where):
        self._openTables()
        result = set(row['gismu'] for row in self.definitions.select('gismu', **where))
        self._closeTables()

        return result

    def create(self, gismu):
        self._openTables()

        definition = self.definitions.select(gismu=gismu).next()

        rafsi = []
        for row in self.rafsi.select('rafsi', gismu=gismu):
            rafsi.append(row['rafsi'])

        keywords = defaultdict(set)
        for row in self.keywords.select('place', 'keyword', gismu=gismu):
            keywords[int(row['place'])].add(row['keyword'])


        obj = Gismu(gismu,
                    definition['definition'],
                    definition['comments'],
                    definition['xrefs'],
                    rafsi,
                    keywords)

        for row in self.chinese.select(gismu=gismu):
            obj.addSourceword(ChineseSourceword(row))

        for row in self.hindi.select(gismu=gismu):
            obj.addSourceword(HindiSourceword(row))

        for row in self.arabic.select(gismu=gismu):
            obj.addSourceword(ArabicSourceword(row))

        for row in self.russian.select(gismu=gismu):
            obj.addSourceword(RussianSourceword(row))

        for row in self.spanish.select(gismu=gismu):
            obj.addSourceword(SpanishSourceword(row))

        for row in self.english.select(gismu=gismu):
            obj.addSourceword(EnglishSourceword(row))

        self._closeTables()

        return obj
