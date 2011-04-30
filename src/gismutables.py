from gismuscore import score

##
# Database table.
#
class Table(object):
    def __init__(self, connection, tablename, attributes):
        self.connection = connection
        self.tablename = tablename
        self.attributes = attributes
        self.cursor = None

    def open(self):
        self.cursor = self.connection.cursor()

    def create(self):
        self.cursor.execute('create table if not exists %s (%s)' % (
                self.tablename,
                ', '.join(['%s text' % attribute
                           for attribute in self.attributes])))

    def insert(self, fields):
        names, values = [], []
        for name, value in fields.iteritems():
            if name in self.attributes:
                names.append(name)
                values.append(value)

        sql = 'insert into %s (%s) values (%s)' % (
            self.tablename,
            ', '.join(names),
            ', '.join(['?'] * len(values)))

        self.cursor.execute(sql, tuple(values))

    def select(self, *attributes, **where):
        if not attributes:
            attributes = self.attributes

        sql = 'select %s from %s' % (
            ', '.join(attributes),
            self.tablename)

        if where:
            names, values = [], []
            for name, value in where.iteritems():
                if name in self.attributes:
                    names.append(name)
                    values.append(value)

            sql += ' where ' + ' and '.join(
                '%s = ?' % name for name in names)

            result = self.cursor.execute(sql, tuple(values))
        else:
            result = self.cursor.execute(sql)

        for row in result:
            yield dict(zip(attributes, row))

    def commit(self):
        self.connection.commit()

    def close(self):
        self.cursor.close()

##
# Table of lojban sourcewords.
#
class SourcewordTable(Table):
    def insert(self, fields):
        if 'transcription' in fields:
            fields['score'] = score(fields['gismu'], fields['transcription'])
        super(SourcewordTable, self).insert(fields)

##
# Table of gismu definitions.
#
class DefinitionTable(Table):
    def __init__(self, connection):
        super(DefinitionTable, self).__init__(
            connection,
            'Definitions',
            ['gismu', 'definition', 'comments', 'xrefs'])

##
# Table with gismu hintwords.
#
class HintwordTable(Table):
    def __init__(self, connection):
        super(HintwordTable, self).__init__(
            connection,
            'Hintwords',
            ['gismu', 'hintword'])

##
# Table associating gismu with textbook chapters.
#
class TextbookTable(Table):
    def __init__(self, connection):
        super(TextbookTable, self).__init__(
            connection,
            'Textbook',
            ['gismu', 'textbook'])

##
# Table with gismu frequencies.
#
class FrequencyTable(Table):
    def __init__(self, connection):
        super(FrequencyTable, self).__init__(
            connection,
            'Frequency',
            ['gismu', 'frequency'])

##
# Table with rafsi.
#
class RafsiTable(Table):
    def __init__(self, connection):
        super(RafsiTable, self).__init__(
            connection,
            'Rafsi',
            ['gismu', 'rafsi'])

    def insert(self, fields):
        for name in ['cvc', 'ccv', 'cvv']:
            rafsi = fields.get(name)
            if rafsi:
                super(RafsiTable, self).insert(
                    dict(gismu=fields['gismu'],
                         rafsi=rafsi))

##
# Table with gismu keywords.
#
class KeywordTable(Table):
    def __init__(self, connection):
        super(KeywordTable, self).__init__(
            connection,
            'Keywords',
            ['gismu', 'place', 'keyword'])

    def insert(self, fields):
        super(KeywordTable, self).insert(
            dict(gismu=fields['gismu'],
                 place=1,
                 keyword=fields['keyword']))

##
# Table with Arabic etymology.
#
class ArabicTable(SourcewordTable):
    def __init__(self, connection):
        super(ArabicTable, self).__init__(
            connection,
            'Arabic',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'transliteration', 'translation', 'comment', 'score'])

##
# Table with Chinese etymology.
#
class ChineseTable(SourcewordTable):
    def __init__(self, connection):
        super(ChineseTable, self).__init__(
            connection,
            'Chinese',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'alternative', 'transliteration', 'translation', 'comment',
             'score'])

##
# Table with English etymology.
#
class EnglishTable(SourcewordTable):
    def __init__(self, connection):
        super(EnglishTable, self).__init__(
            connection,
            'English',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'comment', 'score'])

##
# Table with Hindi etymology.
#
class HindiTable(SourcewordTable):
    def __init__(self, connection):
        super(HindiTable, self).__init__(
            connection,
            'Hindi',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'transliteration', 'translation', 'class', 'comment', 'score'])

##
# Table with Russian etymology.
#
class RussianTable(SourcewordTable):
    def __init__(self, connection):
        super(RussianTable, self).__init__(
            connection,
            'Russian',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'transliteration', 'translation', 'comment', 'score'])

##
# Table with Spanish etymology.
#
class SpanishTable(SourcewordTable):
    def __init__(self, connection):
        super(SpanishTable, self).__init__(
            connection,
            'Spanish',
            ['gismu', 'keyword', 'transcription', 'sourceword',
             'translation', 'comment', 'score'])

##
# Table of cmavo definitions.
#
class CmavoTable(Table):
    def __init__(self, connection):
        super(CmavoTable, self).__init__(
            connection,
            'Cmavo',
            ['cmavo', 'selmao', 'keyword', 'definition', 'comment'])

